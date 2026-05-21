"""File to generate a Dockerfile for a Python application."""
START_OF_TEMPLATE = """# Help

# To execute Python code in the container:
    # docker exec manager python3 --version

# To start an interactive python shell:
    # docker exec -it manager python3

FROM python:PYTHON_VERSION-bookworm

WORKDIR /usr/src/app

# Install system dependencies (no-install-recommends keeps the image lean and the
# apt layer cache stable across rebuilds when only the pip layer below changes).
RUN apt-get update && apt-get install -y --no-install-recommends \\
    git \\
    curl \\
    build-essential \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install extra dependencies
RUN pip install DEPENDENCY_STACK EXTRA_DEPENDENCIES
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
