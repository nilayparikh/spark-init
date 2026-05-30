#!/usr/bin/env python3
"""Print system, CPU, memory, NVIDIA, and CUDA compatibility information.

The script prefers standard-library probes and uses optional tools when they are
available:
- psutil for richer CPU and memory stats
- nvidia-smi for GPU, driver, and CUDA driver-ceiling information
- nvcc for installed CUDA toolkit version
- torch for PyTorch CUDA details
"""

from __future__ import annotations

import importlib.util
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import psutil  # type: ignore
except ImportError:
    psutil = None


def print_section(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def print_kv(items: list[tuple[str, str | None]], indent: int = 0) -> None:
    pad = " " * indent
    for key, value in items:
        if value is None or value == "":
            continue
        print(f"{pad}{key}: {value}")


def clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


def format_bytes(value: int | float | None) -> str | None:
    if value is None:
        return None

    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    size = float(value)
    for unit in units:
        if abs(size) < 1024.0 or unit == units[-1]:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} EiB"


def format_mhz(value: float | int | None) -> str | None:
    if value is None:
        return None
    return f"{value:.1f} MHz" if isinstance(value, float) else f"{value} MHz"


def run_command(args: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(args, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None


def command_stdout(args: list[str]) -> str | None:
    completed = run_command(args)
    if completed is None:
        return None
    return clean_text(completed.stdout)


def pretty_label(tag: str) -> str:
    label = tag.replace("_", " ").replace(".", " ").strip().title()
    replacements = {
        "Gpu": "GPU",
        "Cpu": "CPU",
        "Uuid": "UUID",
        "Pci": "PCI",
        "Cuda": "CUDA",
        "Mig": "MIG",
        "Nvml": "NVML",
        "Sm": "SM",
        "Bar1": "BAR1",
        "Fb": "FB",
        "Id": "ID",
    }
    for source, target in replacements.items():
        label = label.replace(source, target)
    return label


def print_xml_tree(element: ET.Element, indent: int = 0) -> None:
    pad = " " * indent
    label = pretty_label(element.tag)
    children = list(element)
    text = clean_text(element.text)
    attributes = ", ".join(
        f"{pretty_label(key)}={value}" for key, value in element.attrib.items()
    )

    headline = label
    if text:
        headline = f"{headline}: {text}"
    elif not children and not attributes:
        print(f"{pad}{headline}")
        return

    if attributes:
        headline = f"{headline} [{attributes}]"

    print(f"{pad}{headline}")
    for child in children:
        print_xml_tree(child, indent + 2)


def read_text(path: Path) -> str | None:
    try:
        return clean_text(path.read_text(errors="ignore"))
    except OSError:
        return None


def get_system_info() -> list[tuple[str, str | None]]:
    uname = platform.uname()
    python_version = sys.version.split()[0]
    uptime = None
    if psutil is not None:
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = max(0, int(time.time() - boot_time))
            days, remainder = divmod(uptime_seconds, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f"{days}d {hours}h {minutes}m {seconds}s"
        except Exception:
            uptime = None

    items = [
        ("Hostname", socket.gethostname()),
        ("User", os.environ.get("USER") or os.environ.get("LOGNAME")),
        ("OS", f"{uname.system} {uname.release}".strip()),
        ("Kernel", uname.version),
        ("Architecture", uname.machine),
        ("Platform", platform.platform()),
        ("Python", python_version),
        ("Executable", sys.executable),
        ("Uptime", uptime),
    ]
    return items


def get_cpuinfo_block() -> dict[str, str]:
    cpuinfo = Path("/proc/cpuinfo")
    if not cpuinfo.exists():
        return {}

    block: dict[str, str] = {}
    try:
        for line in cpuinfo.read_text(errors="ignore").splitlines():
            if not line.strip():
                if block:
                    break
                continue
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            block[key.strip()] = value.strip()
    except OSError:
        return {}
    return block


def get_lscpu_info() -> list[tuple[str, str]]:
    if shutil.which("lscpu") is None:
        return []

    completed = run_command(["lscpu"])
    if completed is None or completed.returncode != 0:
        return []

    items: list[tuple[str, str]] = []
    for line in (completed.stdout or "").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = clean_text(key) or key.strip()
        value = clean_text(value) or value.strip()
        items.append((key, value))
    return items


def get_lscpu_value(items: list[tuple[str, str]], key: str) -> str | None:
    for current_key, value in items:
        if current_key.lower() == key.lower():
            return value
    return None


def get_lscpu_values(items: list[tuple[str, str]], key: str) -> list[str]:
    values: list[str] = []
    seen: set[str] = set()
    for current_key, value in items:
        if current_key.lower() != key.lower():
            continue
        if value in seen:
            continue
        seen.add(value)
        values.append(value)
    return values


def get_cpu_info(lscpu_info: list[tuple[str, str]] | None = None) -> list[tuple[str, str | None]]:
    cpuinfo = get_cpuinfo_block()
    physical_cores = None
    logical_cores = None
    cpu_freq = None
    per_core_usage = None
    load_avg = None
    ram_total = None
    ram_available = None
    ram_used = None
    ram_percent = None
    swap_total = None
    swap_used = None
    swap_percent = None

    if psutil is not None:
        try:
            physical_cores = str(psutil.cpu_count(logical=False) or "Unknown")
            logical_cores = str(psutil.cpu_count(logical=True) or os.cpu_count() or "Unknown")
        except Exception:
            logical_cores = str(os.cpu_count() or "Unknown")

        try:
            freq = psutil.cpu_freq()
            if freq is not None:
                cpu_freq = (
                    f"current {format_mhz(freq.current)}, min {format_mhz(freq.min)}, max {format_mhz(freq.max)}"
                )
        except Exception:
            cpu_freq = None

        try:
            per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            if per_core:
                per_core_usage = ", ".join(f"CPU {idx}: {usage:.1f}%" for idx, usage in enumerate(per_core))
        except Exception:
            per_core_usage = None

        try:
            vm = psutil.virtual_memory()
            ram_total = format_bytes(vm.total)
            ram_available = format_bytes(vm.available)
            ram_used = format_bytes(vm.used)
            ram_percent = f"{vm.percent:.1f}%"
        except Exception:
            pass

        try:
            sm = psutil.swap_memory()
            swap_total = format_bytes(sm.total)
            swap_used = format_bytes(sm.used)
            swap_percent = f"{sm.percent:.1f}%"
        except Exception:
            pass

        try:
            load = os.getloadavg()
            load_avg = f"1m {load[0]:.2f}, 5m {load[1]:.2f}, 15m {load[2]:.2f}"
        except (AttributeError, OSError):
            load_avg = None
    else:
        logical_cores = str(os.cpu_count() or "Unknown")

    lscpu_model_names = get_lscpu_values(lscpu_info or [], "Model name")
    model = (
        " / ".join(lscpu_model_names)
        if lscpu_model_names
        else cpuinfo.get("model name")
        or cpuinfo.get("Hardware")
        or platform.processor()
        or "Unknown"
    )
    vendor = get_lscpu_value(lscpu_info or [], "Vendor ID") or cpuinfo.get("vendor_id") or cpuinfo.get("CPU implementer")
    architecture = get_lscpu_value(lscpu_info or [], "Architecture") or platform.machine() or "Unknown"
    flags = cpuinfo.get("flags")
    cache_size = cpuinfo.get("cache size")
    cpu_mhz = cpuinfo.get("cpu MHz")

    items = [
        ("Model", model),
        ("Vendor", vendor),
        ("Architecture", architecture),
        ("Physical cores", physical_cores),
        ("Logical cores", logical_cores),
        ("CPU frequency", cpu_freq),
        ("Current MHz", cpu_mhz and f"{cpu_mhz} MHz"),
        ("Cache size", cache_size),
        ("Load average", load_avg),
        ("Per-core usage", per_core_usage),
        ("Flags", flags),
        ("RAM total", ram_total),
        ("RAM available", ram_available),
        ("RAM used", ram_used),
        ("RAM used percent", ram_percent),
        ("Swap total", swap_total),
        ("Swap used", swap_used),
        ("Swap used percent", swap_percent),
    ]
    return items


def get_meminfo_fallback() -> list[tuple[str, str]]:
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        return []

    wanted = {
        "MemTotal": "Total",
        "MemAvailable": "Available",
        "MemFree": "Free",
        "Buffers": "Buffers",
        "Cached": "Cached",
        "SwapTotal": "Swap total",
        "SwapFree": "Swap free",
    }
    values: dict[str, str] = {}
    try:
        for line in meminfo.read_text(errors="ignore").splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key not in wanted:
                continue
            number = re.findall(r"\d+", value)
            if not number:
                continue
            values[wanted[key]] = format_bytes(int(number[0]) * 1024) or value.strip()
    except OSError:
        return []

    return list(values.items())


def parse_nvidia_header(text: str | None) -> dict[str, str | None]:
    if not text:
        return {}

    for line in text.splitlines():
        if "Driver Version" not in line or "CUDA Version" not in line:
            continue
        match = re.search(
            r"NVIDIA-SMI\s+(?P<nvidia_smi_version>\S+).*Driver Version:\s+(?P<driver_version>\S+).*CUDA Version:\s+(?P<cuda_version>\S+)",
            line,
        )
        if match:
            return match.groupdict()
    return {}


def parse_major_minor(version: str | None) -> tuple[int, int] | None:
    if not version:
        return None
    parts = re.findall(r"\d+", version)
    if not parts:
        return None
    major = int(parts[0])
    minor = int(parts[1]) if len(parts) > 1 else 0
    return major, minor


def compare_major_minor(left: str | None, right: str | None) -> int | None:
    left_version = parse_major_minor(left)
    right_version = parse_major_minor(right)
    if left_version is None or right_version is None:
        return None
    if left_version < right_version:
        return -1
    if left_version > right_version:
        return 1
    return 0


def extract_nvcc_version() -> str | None:
    completed = run_command(["nvcc", "--version"])
    if completed is None or completed.returncode != 0:
        return None

    output = completed.stdout or ""
    match = re.search(r"release\s+(\d+\.\d+)", output)
    if match:
        return match.group(1)
    return clean_text(output)


def extract_proc_driver_version() -> str | None:
    version_file = Path("/proc/driver/nvidia/version")
    if not version_file.exists():
        return None

    text = read_text(version_file)
    if not text:
        return None

    match = re.search(r"Kernel Module\s+([0-9.]+)", text)
    if match:
        return match.group(1)
    return text


def extract_nvidia_xml() -> tuple[ET.Element | None, str | None]:
    if shutil.which("nvidia-smi") is None:
        return None, "nvidia-smi was not found on PATH"

    completed = run_command(["nvidia-smi", "-q", "-x"])
    if completed is None:
        return None, "nvidia-smi was not found on PATH"

    xml_text = clean_text(completed.stdout)
    if not xml_text:
        error = clean_text(completed.stderr) or "nvidia-smi -q -x returned no output"
        return None, error

    if not xml_text.lstrip().startswith("<"):
        error = clean_text(completed.stderr) or xml_text
        return None, error

    try:
        return ET.fromstring(xml_text), None
    except ET.ParseError as exc:
        return None, f"failed to parse nvidia-smi XML: {exc}"


def extract_nvidia_list() -> str | None:
    if shutil.which("nvidia-smi") is None:
        return None
    completed = run_command(["nvidia-smi", "-L"])
    if completed is None or completed.returncode != 0:
        return None
    return clean_text(completed.stdout)


def get_torch_cuda_info(driver_cuda_ceiling: str | None) -> list[tuple[str, str | None]]:
    if importlib.util.find_spec("torch") is None:
        return []

    try:
        import torch  # type: ignore
    except Exception:
        return []

    items: list[tuple[str, str | None]] = [
        ("Torch version", getattr(torch, "__version__", None)),
        ("Compile-time CUDA", getattr(getattr(torch, "version", None), "cuda", None)),
        ("CUDA available", str(torch.cuda.is_available())),
        ("Device count", str(torch.cuda.device_count())),
    ]

    cudnn_version = None
    try:
        cudnn_version = torch.backends.cudnn.version()
    except Exception:
        cudnn_version = None
    if cudnn_version is not None:
        items.append(("cuDNN version", str(cudnn_version)))

    compile_time_cuda = getattr(getattr(torch, "version", None), "cuda", None)
    if driver_cuda_ceiling and compile_time_cuda:
        comparison = compare_major_minor(compile_time_cuda, driver_cuda_ceiling)
        if comparison is None:
            status = "unknown"
        elif comparison <= 0:
            status = "compatible"
        else:
            status = "driver too old"
        items.append(("Compatibility vs driver ceiling", status))

    if torch.cuda.is_available():
        for index in range(torch.cuda.device_count()):
            try:
                props = torch.cuda.get_device_properties(index)
                items.extend(
                    [
                        (f"Device {index} name", props.name),
                        (f"Device {index} capability", f"{props.major}.{props.minor}"),
                        (f"Device {index} total memory", format_bytes(props.total_memory)),
                        (f"Device {index} multiprocessors", str(props.multi_processor_count)),
                        (f"Device {index} max threads per block", str(props.max_threads_per_block)),
                    ]
                )
                allocated = None
                reserved = None
                try:
                    allocated = format_bytes(torch.cuda.memory_allocated(index))
                    reserved = format_bytes(torch.cuda.memory_reserved(index))
                except Exception:
                    pass
                items.append((f"Device {index} allocated memory", allocated))
                items.append((f"Device {index} reserved memory", reserved))
            except Exception:
                continue

    return items


def get_cuda_env_info() -> list[tuple[str, str | None]]:
    keys = ["CUDA_HOME", "CUDA_PATH", "CUDA_VISIBLE_DEVICES", "NVIDIA_VISIBLE_DEVICES"]
    return [(key, os.environ.get(key)) for key in keys]


def main() -> int:
    lscpu_info = get_lscpu_info()

    print_section("System")
    print_kv(get_system_info())

    print_section("CPU")
    print_kv(get_cpu_info(lscpu_info))

    if lscpu_info:
        print()
        print("lscpu")
        print("-----")
        print_kv(lscpu_info, indent=2)

    cpuinfo = get_cpuinfo_block()
    if cpuinfo:
        summary_keys = [
            ("Model name", cpuinfo.get("model name")),
            ("Vendor ID", cpuinfo.get("vendor_id")),
            ("CPU family", cpuinfo.get("cpu family")),
            ("Model", cpuinfo.get("model")),
            ("Stepping", cpuinfo.get("stepping")),
            ("Microcode", cpuinfo.get("microcode")),
            ("Cache size", cpuinfo.get("cache size")),
            ("Bogomips", cpuinfo.get("bogomips")),
            ("Address sizes", cpuinfo.get("address sizes")),
            ("Flags", cpuinfo.get("flags")),
        ]
        print()
        print("/proc/cpuinfo")
        print("-------------")
        print_kv(summary_keys, indent=2)

    print_section("Memory")
    memory_items: list[tuple[str, str]] = []
    if psutil is not None:
        try:
            vm = psutil.virtual_memory()
            memory_items.extend(
                [
                    ("Total", format_bytes(vm.total) or "Unknown"),
                    ("Available", format_bytes(vm.available) or "Unknown"),
                    ("Used", format_bytes(vm.used) or "Unknown"),
                    ("Percent used", f"{vm.percent:.1f}%"),
                ]
            )
        except Exception:
            pass

        try:
            swap = psutil.swap_memory()
            memory_items.extend(
                [
                    ("Swap total", format_bytes(swap.total) or "Unknown"),
                    ("Swap used", format_bytes(swap.used) or "Unknown"),
                    ("Swap percent", f"{swap.percent:.1f}%"),
                ]
            )
        except Exception:
            pass
    else:
        memory_items.extend(get_meminfo_fallback())

    if not memory_items:
        memory_items.append(("Memory", "Unavailable"))
    print_kv(memory_items)

    print_section("NVIDIA")
    header_text = command_stdout(["nvidia-smi"]) if shutil.which("nvidia-smi") else None
    header = parse_nvidia_header(header_text)
    root, xml_error = extract_nvidia_xml()
    proc_driver_version = extract_proc_driver_version()
    nvidia_list = extract_nvidia_list()

    nvidia_items = [
        ("NVIDIA-SMI version", header.get("nvidia_smi_version") if header else None),
        (
            "Driver version",
            (header.get("driver_version") if header else None)
            or (root.findtext("driver_version") if root is not None else None)
            or proc_driver_version,
        ),
        (
            "Driver-reported CUDA ceiling",
            (header.get("cuda_version") if header else None)
            or (root.findtext("cuda_version") if root is not None else None),
        ),
        ("Attached GPUs", root.findtext("attached_gpus") if root is not None else None),
        ("Driver version file", proc_driver_version),
    ]
    print_kv(nvidia_items)

    if root is not None:
        extra_root_items = [child for child in list(root) if child.tag != "gpu"]
        if extra_root_items:
            print()
            print("NVIDIA root details")
            print("-------------------")
            for child in extra_root_items:
                print_xml_tree(child, indent=2)

        gpu_nodes = list(root.findall("gpu"))
        if gpu_nodes:
            print()
            print("GPU details")
            print("-----------")
            for index, gpu in enumerate(gpu_nodes):
                gpu_name = clean_text(gpu.findtext("product_name")) or "Unknown GPU"
                gpu_uuid = clean_text(gpu.findtext("uuid"))
                bus_id = gpu.attrib.get("id")
                summary_bits = [gpu_name]
                if gpu_uuid:
                    summary_bits.append(gpu_uuid)
                if bus_id:
                    summary_bits.append(bus_id)
                print(f"GPU {index}: {' | '.join(summary_bits)}")
                for child in list(gpu):
                    print_xml_tree(child, indent=2)

    elif nvidia_list:
        print()
        print("GPU list")
        print("--------")
        print(nvidia_list)
    else:
        print()
        print("NVIDIA GPU details are unavailable")
        print("----------------------------------")
        if xml_error:
            print(xml_error)

    driver_cuda_ceiling = None
    if header:
        driver_cuda_ceiling = header.get("cuda_version")
    elif root is not None:
        driver_cuda_ceiling = clean_text(root.findtext("cuda_version"))

    toolkit_version = extract_nvcc_version()
    if toolkit_version is not None or driver_cuda_ceiling is not None:
        print_section("CUDA compatibility")
        compat_items: list[tuple[str, str | None]] = [
            ("Driver ceiling", driver_cuda_ceiling),
            ("nvcc toolkit version", toolkit_version),
        ]

        comparison = compare_major_minor(toolkit_version, driver_cuda_ceiling)
        if comparison is None:
            compat_status = "unknown"
        elif comparison <= 0:
            compat_status = "compatible"
        else:
            compat_status = "driver too old for the detected toolkit"
        compat_items.append(("nvcc vs driver", compat_status))
        print_kv(compat_items)

    cuda_env_items = get_cuda_env_info()
    if any(value is not None for _, value in cuda_env_items):
        print_section("CUDA environment")
        print_kv(cuda_env_items)

    torch_items = get_torch_cuda_info(driver_cuda_ceiling)
    if torch_items:
        print_section("PyTorch CUDA")
        print_kv(torch_items)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())