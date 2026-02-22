"""File to generate a Dockerfile for a Java application."""
START_OF_TEMPLATE = """# Help

# To compile Java code in the container:
    # docker exec manager javac Main.java

# To run a Java program:
    # docker exec manager java Main

# To start an interactive shell:
    # docker exec -it manager bash

FROM eclipse-temurin:JAVA_VERSION-jdk-bookworm

WORKDIR /usr/src/app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    git \\
    curl \\
    build-essential \\
    maven \\
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF-8"
"""

END_OF_TEMPLATE = """
CMD ["bash"]
"""
