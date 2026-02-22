"""File to generate a Dockerfile for a Python application."""
START_OF_TEMPLATE = """# Help

# To execute Python code in the container:
    # docker exec manager python3 --version

# To start an interactive python shell:
    # docker exec -it manager python3

FROM python:PYTHON_VERSION-bookworm

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    python3-dev \\
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1

# Install extra dependencies
RUN pip install DEPENDENCY_STACK EXTRA_DEPENDENCIES
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
