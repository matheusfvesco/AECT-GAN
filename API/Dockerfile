# ============================================================
# AECT-GAN API Dockerfile
# Base: CUDA 12.8 + Python 3.9 with conda
# GPU-enabled via nvidia-container-toolkit
# ============================================================

FROM nvidia/cuda:12.8.0-runtime-ubuntu22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    bzip2 \
    ca-certificates \
    zlib1g-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda3
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH="/opt/conda/bin:$PATH"

# Create conda environment from environment.yml
WORKDIR /app

COPY environment.yml /app/environment.yml

# Accept Anaconda TOS for defaults channels
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Create conda environment
RUN conda env create -f /app/environment.yml -p /opt/conda/envs/aect_env_api && \
    conda clean -afy

# Activate the environment
ENV PATH="/opt/conda/envs/aect_env_api/bin:$PATH"
ENV CONDA_DEFAULT_ENV=aect_env_api
ENV CONDA_PREFIX=/opt/conda/envs/aect_env_api
ENV PYTHONPATH=/app

# nnUNet and threading environment variables to limit multiprocessing
ENV nnUNet_n_proc=0
ENV OMP_NUM_THREADS=1
ENV MKL_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1

# Copy application code
COPY . /app/

# Create uploads directory
RUN mkdir -p /app/uploads

# Symlink weights directory for backward compatibility with relative paths
RUN mkdir -p /app/API && ln -s /app/weights /app/API/weights

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/ || exit 1

# Run the API
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
