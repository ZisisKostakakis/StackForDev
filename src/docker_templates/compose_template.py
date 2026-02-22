"""docker-compose.yml template for development environments."""

COMPOSE_TEMPLATE = """\
services:
  dev:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: {project_name}-dev
    volumes:
      - .:/usr/src/app
    working_dir: /usr/src/app
    stdin_open: true
    tty: true
"""

DOCKERIGNORE_TEMPLATE = """\
__pycache__
*.pyc
*.pyo
.env
.env.*
.git
.gitignore
node_modules
*.dockerfile
*.log
.DS_Store
dist/
build/
"""
