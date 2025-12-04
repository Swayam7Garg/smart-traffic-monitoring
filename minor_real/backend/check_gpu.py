"""
Quick script to check if GPU is available for PyTorch
Run this after CUDA PyTorch installation completes
"""

import torch

print("=" * 50)
print("GPU AVAILABILITY CHECK")
print("=" * 50)

# Check CUDA availability
cuda_available = torch.cuda.is_available()
print(f"\n✓ CUDA Available: {cuda_available}")

if cuda_available:
    # GPU details
    gpu_count = torch.cuda.device_count()
    print(f"✓ Number of GPUs: {gpu_count}")
    
    for i in range(gpu_count):
        gpu_name = torch.cuda.get_device_name(i)
        print(f"  GPU {i}: {gpu_name}")
        
        # Memory info
        memory_allocated = torch.cuda.memory_allocated(i) / (1024**3)
        memory_reserved = torch.cuda.memory_reserved(i) / (1024**3)
        total_memory = torch.cuda.get_device_properties(i).total_memory / (1024**3)
        
        print(f"    Total Memory: {total_memory:.2f} GB")
        print(f"    Allocated: {memory_allocated:.2f} GB")
        print(f"    Reserved: {memory_reserved:.2f} GB")
    
    # Test tensor on GPU
    print("\n✓ Testing GPU tensor creation...")
    x = torch.rand(1000, 1000).cuda()
    print(f"  Tensor device: {x.device}")
    print(f"  Tensor shape: {x.shape}")
    
    print("\n🚀 GPU is ready for YOLOv8 acceleration!")
    print("   Expected speedup: 10-15x faster processing")
    
else:
    print("\n❌ CUDA not available")
    print("   Possible reasons:")
    print("   1. CUDA PyTorch not installed (install with: pip install torch --index-url https://download.pytorch.org/whl/cu118)")
    print("   2. No NVIDIA GPU detected")
    print("   3. CUDA drivers not installed")
    print("\n   Current PyTorch version:", torch.__version__)

print("\n" + "=" * 50)
