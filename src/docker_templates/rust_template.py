"""File to generate a Dockerfile for a Rust application."""
START_OF_TEMPLATE = """# Help

# To compile and run Rust code in the container:
    # docker exec manager cargo build
    # docker exec manager cargo run

# To start an interactive shell:
    # docker exec -it manager bash

FROM rust:RUST_VERSION-bookworm

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    pkg-config \\
    libssl-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install Cargo packages
RUN cargo install DEPENDENCY_STACK EXTRA_DEPENDENCIES
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
