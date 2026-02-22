"""File to generate a Dockerfile for a JavaScript/Node.js application."""
START_OF_TEMPLATE = """# Help

# To execute Node.js code in the container:
    # docker exec manager node --version

# To start an interactive Node.js shell:
    # docker exec -it manager node

FROM node:NODE_VERSION-bookworm

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

# Install global packages
RUN npm install -g DEPENDENCY_STACK EXTRA_DEPENDENCIES
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
