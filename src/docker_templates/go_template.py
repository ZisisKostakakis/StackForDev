"""File to generate a Dockerfile for a Go application."""
START_OF_TEMPLATE = """# Help

# To execute Go code in the container:
    # docker exec manager go version

# To start an interactive shell:
    # docker exec -it manager bash

FROM golang:GO_VERSION-bullseye

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install Go packages
RUN go install DEPENDENCY_STACK EXTRA_DEPENDENCIES
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
