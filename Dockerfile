# ---------------------------------------------------------
# ES-PTAM Docker environment (Ubuntu 20.04 + ROS Noetic)
# ---------------------------------------------------------

FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------
# 1. Basic dependencies + ROS repo
# -----------------------------
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release && \
    curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add - && \
    sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros1.list'

RUN apt-get update && apt-get install -y \
    wget \
    git \
    openssh-client \
    ca-certificates \
    build-essential \
    cmake \
    pkg-config \
    python3 \
    python3-pip \
    python-is-python3 \
    python3-vcstool \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 2. Install ROS Noetic
# -----------------------------

RUN apt-get update && apt-get install -y \
    ros-noetic-desktop-full \
    python3-rosdep \
    python3-catkin-tools \
    && rm -rf /var/lib/apt/lists/*

RUN rosdep init && rosdep update

# -----------------------------
# 3. Additional ES-PTAM deps
# -----------------------------
# libcaer-dev is not shipped in Ubuntu's default repos, so build from source.
RUN apt-get update && apt-get install -y \
    ros-noetic-image-geometry \
    ros-noetic-tf-conversions \
    ros-noetic-camera-info-manager \
    ros-noetic-sophus \
    libusb-1.0-0-dev \
    libserialport-dev \
    python2.7 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ros-noetic-image-view \
    ros-noetic-pcl-ros \
 && rm -rf /var/lib/apt/lists/*


RUN git clone --depth 1 https://gitlab.com/inivation/libcaer.git /tmp/libcaer && \
    cd /tmp/libcaer && \
    cmake -B build -S . -DCMAKE_BUILD_TYPE=Release && \
    cmake --build build --target install -j"$(nproc)" && \
    ldconfig && \
    rm -rf /tmp/libcaer


# -----------------------------
# 4. Setup catkin workspace
# -----------------------------
RUN mkdir -p /root/catkin_ws/src

# -----------------------------
# 5. Copy your ES-PTAM fork
# -----------------------------
# 5. Copy your ES-PTAM fork
WORKDIR /root/catkin_ws/src
COPY . /root/catkin_ws/src/ES-PTAM

# Fix Windows CRLF line endings for Python scripts
RUN apt-get update && apt-get install -y dos2unix && \
    find /root/catkin_ws/src/ES-PTAM -type f \( -name "*.py" -o -name "rqt_evo" \) -print0 | xargs -0 dos2unix

# Download dependent repos using dependencies.yaml
RUN vcs-import < ES-PTAM/dependencies.yaml

# -----------------------------
# 6. Build the workspace
# -----------------------------
WORKDIR /root/catkin_ws
RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin config --init --mkdirs --extend /opt/ros/noetic --merge-devel --cmake-args -DCMAKE_BUILD_TYPE=Release"

RUN /bin/bash -c "source /opt/ros/noetic/setup.bash && catkin build dvs_tracking mapper_emvs_stereo"

# Source environment at container startup
CMD ["/bin/bash", "-c", "source /root/catkin_ws/devel/setup.bash && bash"]
