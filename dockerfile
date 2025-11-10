# Base image
FROM ubuntu:22.04

# Avoid timezone and locale prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update packages and install essentials
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    vim git curl wget build-essential \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and setuptools
RUN pip install --upgrade pip setuptools wheel

# Make a workspace
WORKDIR /workspace

# Copy your project into the container (optional)
COPY . /workspace

# Install your project dependencies if you have them
# The --break-system-packages and --no-deps flags allow forced installs
RUN if [ -f requirements.txt ]; then \
      pip install --no-cache-dir --break-system-packages --no-deps -r requirements.txt || true; \
    fi

# Expose Streamlit’s default port for later use
EXPOSE 8501

# Default command drops you into a bash shell for development
CMD ["/bin/bash"]
