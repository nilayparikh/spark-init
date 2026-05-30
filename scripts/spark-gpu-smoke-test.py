import torch
import time
import sys

print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"Device Name: {torch.cuda.get_device_name(0)}")

try:
    # Step 1: Simulate the Model Tensor Load in VRAM
    print("\n[1/3] Simulating Model Weight allocation in VRAM...")
    dummy_weights = torch.randn(5000, 5000, dtype=torch.bfloat16, device="cuda")
    torch.cuda.synchronize()

    # Step 2: Simulate the exact Host RAM pinning that caused the driver panic
    print("[2/3] Simulating Host Pinned Memory Allocation (Driver Workspace)...")
    # Allocate 32GB of pinned contiguous system memory mimicking FlashInfer tables
    host_pinned = torch.empty(8 * 1024 * 1024 * 1024, dtype=torch.float32).pin_memory()

    # Step 3: Run a basic forward pass stress loop
    print("[3/3] Running execution loop to stress hardware power draw...")
    for i in range(10):
        # Simple massive matrix multiplication to force sudden power pull
        a = torch.randn(8192, 8192, dtype=torch.bfloat16, device="cuda")
        b = torch.randn(8192, 8192, dtype=torch.bfloat16, device="cuda")
        c = torch.matmul(a, b)
        torch.cuda.synchronize()
        print(f"    Loop {i+1}/10 completed successfully.")
        time.sleep(0.5)

    print("\nDIAGNOSTIC PASSED: The hardware and base NVIDIA driver are operating normally!")
    sys.exit(0)

except Exception as e:
    print(f"\nDIAGNOSTIC FAILED: {str(e)}")
    sys.exit(1)
