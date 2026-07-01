FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-numpy python3-scipy \
    python3-matplotlib python3-pandas \
    zstd wget ca-certificates valgrind \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages numba
WORKDIR /work
