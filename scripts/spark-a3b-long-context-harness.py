#!/usr/bin/env python3
from __future__ import annotations

import argparse
import concurrent.futures
import json
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "http://localhost:8000"
DEFAULT_MODEL = "qwen3.6-35b-a3b-nvfp4"


class ApiRequestError(RuntimeError):
    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"HTTP {status_code}: {body}")


@dataclass
class RequestResult:
    worker_id: int
    iteration: int
    latency_s: float
    prompt_tokens: int | None
    completion_tokens: int | None
    ok: bool
    response_text: str
    error: str | None = None


def http_json(method: str, url: str, payload: dict[str, Any] | None, timeout_s: float) -> tuple[dict[str, Any], str]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout_s) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ApiRequestError(exc.code, body or exc.reason) from exc

    if not body:
        return {}, body
    return json.loads(body), body


def is_context_too_large_error(exc: ApiRequestError) -> bool:
    if exc.status_code != 400:
        return False

    body = exc.body.lower()
    return any(
        marker in body
        for marker in (
            "maximum context length",
            "max context length",
            "max model len",
            "too many tokens",
            "prompt is too long",
            "input is too long",
            "requested tokens",
            "context length",
        )
    )


def wait_for_health(base_url: str, timeout_s: float) -> None:
    deadline = time.monotonic() + timeout_s
    last_error = "service never became healthy"

    while time.monotonic() < deadline:
        try:
            urllib.request.urlopen(f"{base_url}/health", timeout=5).read()
            return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            time.sleep(2)

    raise RuntimeError(f"Timed out waiting for {base_url}/health: {last_error}")


def resolve_model(base_url: str, requested_model: str, timeout_s: float) -> str:
    payload, _ = http_json("GET", f"{base_url}/v1/models", None, timeout_s)
    models = [entry.get("id") for entry in payload.get("data", []) if entry.get("id")]
    if requested_model in models:
        return requested_model
    if models:
        return models[0]
    raise RuntimeError("No models were returned by /v1/models")


def make_expected_values(worker_id: int, iteration: int) -> dict[str, str]:
    stem = f"w{worker_id:02d}-i{iteration:05d}"
    return {
        "primary": f"primary-{stem}-amber-314159",
        "backup": f"backup-{stem}-cobalt-271828",
        "checksum": f"checksum-{stem}-iris-161803",
    }


def filler_line(index: int) -> str:
    return (
        f"Segment {index:05d}: alpha bravo charlie delta echo foxtrot golf hotel india "
        f"juliet kilo lima mango nectar oscar papa quebec romeo sierra tango uniform victor whiskey xray yankee zulu.\n"
    )


def build_prompt(worker_id: int, iteration: int, segment_count: int) -> tuple[str, dict[str, str]]:
    expected = make_expected_values(worker_id, iteration)
    nonce = f"nonce-worker-{worker_id:02d}-iteration-{iteration:05d}-ts-{time.time_ns()}"
    lines = [
        "You are reading a long archive dump.",
        f"Cache bust nonce: {nonce}",
        "The archive contains three target records that must be extracted exactly.",
        "Everything else is filler and should be ignored when answering.",
        "",
    ]

    marker_positions = {
        max(0, segment_count // 6): f"Target Record A: primary={expected['primary']}\n",
        max(0, segment_count // 2): f"Target Record B: backup={expected['backup']}\n",
        max(0, (segment_count * 5) // 6): f"Target Record C: checksum={expected['checksum']}\n",
    }

    for index in range(segment_count):
        special_line = marker_positions.get(index)
        if special_line is not None:
            lines.append(special_line)
        lines.append(filler_line(index))

    lines.extend(
        [
            "",
            "Question:",
            "Return exactly one JSON object with keys primary, backup, and checksum.",
            "Use the exact string values from the three target records.",
            "Do not add markdown, explanations, or extra keys.",
        ]
    )

    return "".join(lines), expected


def create_payload(model: str, prompt: str, max_tokens: int) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "chat_template_kwargs": {"enable_thinking": False},
    }


def extract_message_content(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    return ""


def is_answer_correct(response_text: str, expected: dict[str, str]) -> bool:
    try:
        parsed = json.loads(response_text)
    except json.JSONDecodeError:
        return all(value in response_text for value in expected.values())

    return all(parsed.get(key) == value for key, value in expected.items())


def measure_prompt_tokens(
    base_url: str,
    model: str,
    worker_id: int,
    iteration: int,
    segment_count: int,
    timeout_s: float,
) -> int:
    prompt, _ = build_prompt(worker_id, iteration, segment_count)
    payload, _ = http_json(
        "POST",
        f"{base_url}/v1/chat/completions",
        create_payload(model, prompt, max_tokens=1),
        timeout_s,
    )
    usage = payload.get("usage") or {}
    prompt_tokens = usage.get("prompt_tokens")
    if not isinstance(prompt_tokens, int):
        raise RuntimeError("Could not read usage.prompt_tokens during calibration")
    return prompt_tokens


def try_measure_prompt_tokens(
    base_url: str,
    model: str,
    worker_id: int,
    iteration: int,
    segment_count: int,
    timeout_s: float,
) -> int | None:
    try:
        return measure_prompt_tokens(base_url, model, worker_id, iteration, segment_count, timeout_s)
    except ApiRequestError as exc:
        if is_context_too_large_error(exc):
            return None
        raise


def calibrate_segment_count(
    base_url: str,
    model: str,
    target_prompt_tokens: int,
    tolerance_tokens: int,
    request_timeout_s: float,
) -> tuple[int, int]:
    estimate = max(128, target_prompt_tokens // 40)
    best_segments = estimate
    best_tokens = -1
    best_delta = float("inf")

    def update_best(segments: int, prompt_tokens: int) -> None:
        nonlocal best_segments, best_tokens, best_delta
        delta = abs(prompt_tokens - target_prompt_tokens)
        if delta < best_delta:
            best_delta = delta
            best_segments = segments
            best_tokens = prompt_tokens

    low = max(64, estimate // 2)
    high = max(low + 1, estimate)

    low_tokens = try_measure_prompt_tokens(base_url, model, 0, 0, low, request_timeout_s)
    if low_tokens is None:
        raise RuntimeError("Calibration failed: even the smallest probe exceeded the context window")
    update_best(low, low_tokens)

    prompt_tokens = try_measure_prompt_tokens(base_url, model, 0, 0, high, request_timeout_s)
    while prompt_tokens is None and high > low + 1:
        high = (low + high) // 2
        prompt_tokens = try_measure_prompt_tokens(base_url, model, 0, 0, high, request_timeout_s)

    if prompt_tokens is not None:
        update_best(high, prompt_tokens)

    while prompt_tokens is not None and prompt_tokens < target_prompt_tokens:
        low = high
        high = max(high + 1, int(high * 1.5))
        prompt_tokens = try_measure_prompt_tokens(base_url, model, 0, 0, high, request_timeout_s)
        if prompt_tokens is not None:
            update_best(high, prompt_tokens)
            if abs(prompt_tokens - target_prompt_tokens) <= tolerance_tokens:
                return high, prompt_tokens

    while low <= high:
        middle = (low + high) // 2
        prompt_tokens = try_measure_prompt_tokens(base_url, model, 0, 0, middle, request_timeout_s)

        if prompt_tokens is None:
            high = middle - 1
            continue

        update_best(middle, prompt_tokens)

        if abs(prompt_tokens - target_prompt_tokens) <= tolerance_tokens:
            return middle, prompt_tokens

        if prompt_tokens < target_prompt_tokens:
            low = middle + 1
        else:
            high = middle - 1

    return best_segments, best_tokens


def run_worker(
    worker_id: int,
    base_url: str,
    model: str,
    segment_count: int,
    request_timeout_s: float,
    stop_at: float,
    print_lock: threading.Lock,
) -> list[RequestResult]:
    results: list[RequestResult] = []
    iteration = 1

    while time.monotonic() < stop_at:
        result = perform_request(
            worker_id=worker_id,
            iteration=iteration,
            base_url=base_url,
            model=model,
            segment_count=segment_count,
            request_timeout_s=request_timeout_s,
        )

        results.append(result)

        with print_lock:
            status = "PASS" if result.ok else "FAIL"
            prompt_tokens = result.prompt_tokens if result.prompt_tokens is not None else -1
            completion_tokens = result.completion_tokens if result.completion_tokens is not None else -1
            print(
                f"[{status}] worker={worker_id} iteration={iteration} latency={result.latency_s:.2f}s "
                f"prompt_tokens={prompt_tokens} completion_tokens={completion_tokens}",
                flush=True,
            )
            if result.error:
                print(f"        {result.error}", flush=True)

        iteration += 1

    return results


def perform_request(
    worker_id: int,
    iteration: int,
    base_url: str,
    model: str,
    segment_count: int,
    request_timeout_s: float,
) -> RequestResult:
    prompt, expected = build_prompt(worker_id, iteration, segment_count)
    started_at = time.monotonic()

    try:
        response, _ = http_json(
            "POST",
            f"{base_url}/v1/chat/completions",
            create_payload(model, prompt, max_tokens=96),
            request_timeout_s,
        )
        latency_s = time.monotonic() - started_at
        usage = response.get("usage") or {}
        response_text = extract_message_content(response)
        ok = is_answer_correct(response_text, expected)
        error = None if ok else f"answer mismatch: expected={expected} actual={response_text!r}"
        return RequestResult(
            worker_id=worker_id,
            iteration=iteration,
            latency_s=latency_s,
            prompt_tokens=usage.get("prompt_tokens"),
            completion_tokens=usage.get("completion_tokens"),
            ok=ok,
            response_text=response_text,
            error=error,
        )
    except Exception as exc:  # noqa: BLE001
        latency_s = time.monotonic() - started_at
        return RequestResult(
            worker_id=worker_id,
            iteration=iteration,
            latency_s=latency_s,
            prompt_tokens=None,
            completion_tokens=None,
            ok=False,
            response_text="",
            error=str(exc),
        )


def summarize(results: list[RequestResult]) -> int:
    if not results:
        print("No requests were completed.")
        return 1

    latencies = [item.latency_s for item in results]
    prompt_tokens = [item.prompt_tokens for item in results if isinstance(item.prompt_tokens, int)]
    completion_tokens = [item.completion_tokens for item in results if isinstance(item.completion_tokens, int)]
    failures = [item for item in results if not item.ok]

    print("\n=== Long-Context Harness Summary ===")
    print(f"Total requests: {len(results)}")
    print(f"Successful QA:  {len(results) - len(failures)}")
    print(f"Failed QA:      {len(failures)}")
    print(f"Latency avg:    {statistics.mean(latencies):.2f}s")
    print(f"Latency p50:    {statistics.median(latencies):.2f}s")
    if len(latencies) > 1:
        percentile_95_index = max(0, min(len(latencies) - 1, round((len(latencies) - 1) * 0.95)))
        latency_p95 = sorted(latencies)[percentile_95_index]
        print(f"Latency p95:    {latency_p95:.2f}s")
    if prompt_tokens:
        print(f"Prompt tokens:  min={min(prompt_tokens)} avg={statistics.mean(prompt_tokens):.0f} max={max(prompt_tokens)}")
    if completion_tokens:
        print(
            f"Completion toks:min={min(completion_tokens)} avg={statistics.mean(completion_tokens):.1f} max={max(completion_tokens)}"
        )

    if failures:
        print("\nFailures:")
        for item in failures[:10]:
            print(f"  worker={item.worker_id} iteration={item.iteration}: {item.error}")
        if len(failures) > 10:
            print(f"  ... {len(failures) - 10} more failures omitted")
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run parallel 128K-class QA requests against the local A3B service for an extended soak test."
    )
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"Base URL for the OpenAI-compatible API (default: {DEFAULT_BASE_URL})")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Requested model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--workers", type=int, default=2, help="Number of parallel workers (default: 2)")
    parser.add_argument("--duration-minutes", type=float, default=20.0, help="Soak duration in minutes (default: 20)")
    parser.add_argument(
        "--target-prompt-tokens",
        type=int,
        default=131072,
        help="Target prompt token count for each request (default: 131072)",
    )
    parser.add_argument(
        "--tolerance-tokens",
        type=int,
        default=2048,
        help="Acceptable calibration delta around the target prompt token count (default: 2048)",
    )
    parser.add_argument(
        "--request-timeout-seconds",
        type=float,
        default=900.0,
        help="Per-request timeout in seconds (default: 900)",
    )
    parser.add_argument(
        "--startup-timeout-seconds",
        type=float,
        default=600.0,
        help="How long to wait for localhost health before failing (default: 600)",
    )
    parser.add_argument(
        "--warmup-requests",
        type=int,
        default=1,
        help="Number of single-request warmup passes to run before starting the parallel soak (default: 1)",
    )
    args = parser.parse_args()

    if args.workers < 1:
        parser.error("--workers must be at least 1")
    if args.duration_minutes <= 0:
        parser.error("--duration-minutes must be greater than 0")
    if args.target_prompt_tokens < 4096:
        parser.error("--target-prompt-tokens must be at least 4096")
    if args.tolerance_tokens < 0:
        parser.error("--tolerance-tokens must be non-negative")
    if args.warmup_requests < 0:
        parser.error("--warmup-requests must be non-negative")
    return args


def main() -> int:
    args = parse_args()

    print(f"Waiting for service health at {args.base_url} ...", flush=True)
    wait_for_health(args.base_url, args.startup_timeout_seconds)

    model = resolve_model(args.base_url, args.model, args.request_timeout_seconds)
    print(f"Using model: {model}", flush=True)

    print(
        f"Calibrating prompt size near {args.target_prompt_tokens} tokens using the live API tokenizer ...",
        flush=True,
    )
    segment_count, measured_tokens = calibrate_segment_count(
        args.base_url,
        model,
        args.target_prompt_tokens,
        args.tolerance_tokens,
        args.request_timeout_seconds,
    )
    print(
        f"Calibration complete: segment_count={segment_count} measured_prompt_tokens={measured_tokens}",
        flush=True,
    )

    for warmup_index in range(args.warmup_requests):
        warmup_result = perform_request(
            worker_id=-1,
            iteration=warmup_index + 1,
            base_url=args.base_url,
            model=model,
            segment_count=segment_count,
            request_timeout_s=args.request_timeout_seconds,
        )
        status = "PASS" if warmup_result.ok else "FAIL"
        print(
            f"Warmup {warmup_index + 1}/{args.warmup_requests}: {status} latency={warmup_result.latency_s:.2f}s "
            f"prompt_tokens={warmup_result.prompt_tokens} completion_tokens={warmup_result.completion_tokens}",
            flush=True,
        )
        if warmup_result.error:
            print(f"        {warmup_result.error}", flush=True)
        if not warmup_result.ok:
            print("Warmup failed; aborting soak.", flush=True)
            return 1

    duration_seconds = args.duration_minutes * 60.0
    stop_at = time.monotonic() + duration_seconds
    print(
        f"Starting soak: workers={args.workers} duration_minutes={args.duration_minutes:.2f} base_url={args.base_url}",
        flush=True,
    )

    print_lock = threading.Lock()
    all_results: list[RequestResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [
            executor.submit(
                run_worker,
                worker_id,
                args.base_url,
                model,
                segment_count,
                args.request_timeout_seconds,
                stop_at,
                print_lock,
            )
            for worker_id in range(args.workers)
        ]
        for future in concurrent.futures.as_completed(futures):
            all_results.extend(future.result())

    return summarize(all_results)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        raise SystemExit(130)