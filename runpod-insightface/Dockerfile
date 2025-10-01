# Use the official RunPod PyTorch base image
FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Update apt and install system packages
RUN apt update -y && \
    apt install -y --no-install-recommends \
        nvtop htop btop wget curl ncdu nano rsync \
        ranger jq lftp aria2 zip unzip rhash git && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages
# Note: Use --extra-index-url for CUDA-enabled onnxruntime if needed
RUN pip install --no-cache-dir \
    insightface \
    onnxruntime-gpu \
    opencv-python \
    faiss-cpu

# Create app directory
WORKDIR /app

# Copy your local app code into the container
COPY app/ .

# Optional: Set a default command (e.g., bash)
CMD ["bash"]
