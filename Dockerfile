# Simple base image – ES-PTAM seems to target Ubuntu/ROS-based setups
FROM ubuntu:20.04

# Avoid interactive prompts in apt
ENV DEBIAN_FRONTEND=noninteractive

# Basic build tools and common libs for C++ / vision projects
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    pkg-config \
    libeigen3-dev \
    libboost-all-dev \
    libopencv-dev \
    libpcl-dev \
    python3 \
    python3-pip \
    python3-numpy \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /workspace

# Copy the ES-PTAM source into the container
COPY . /workspace

# (Optional) create a 'build' folder but do NOT compile yet
# You will follow docs/installation.md manually inside the container
RUN mkdir -p /workspace/build

# Default shell
CMD ["/bin/bash"]
