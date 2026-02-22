"""Core Dockerfile generation logic, decoupled from AWS dependencies."""

import re
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.docker_templates import python_template, javascript_template, go_template

TEMPLATE_REGISTRY: dict[str, tuple] = {
    "python": (python_template.START_OF_TEMPLATE, python_template.END_OF_TEMPLATE, "PYTHON_VERSION"),
    "javascript": (javascript_template.START_OF_TEMPLATE, javascript_template.END_OF_TEMPLATE, "NODE_VERSION"),
    "go": (go_template.START_OF_TEMPLATE, go_template.END_OF_TEMPLATE, "GO_VERSION"),
}

SUPPORTED_LANGUAGES = set(TEMPLATE_REGISTRY.keys())

STACK_PACKAGES: dict[str, str] = {
    # Python
    "Django Stack": "django djangorestframework psycopg2-binary Pillow djangorestframework-simplejwt requests",
    "Flask Stack": "flask flask-restful flask-sqlalchemy flask-migrate requests",
    "Data Science Stack": "pandas numpy matplotlib scikit-learn jupyter",
    "Web Scraping Stack": "beautifulsoup4 scrapy requests lxml pandas",
    "Machine Learning Stack": "scikit-learn tensorflow keras numpy matplotlib",
    # JavaScript (npm global packages)
    "Express Stack": "express mongoose body-parser cors dotenv",
    "React Stack": "react react-router redux axios",
    "Vue.js Stack": "vue@latest vue-router vuex axios",
    "Node.js API Stack": "express mongoose jsonwebtoken",
    "Full-Stack JavaScript": "express mongoose react redux",
    # Go (go install paths)
    "Gin Stack": "github.com/gin-gonic/gin@latest",
    "Beego Stack": "github.com/beego/beego/v2@latest",
    "Web Framework Stack": "github.com/labstack/echo/v4@latest",
    "Microservices Stack": "github.com/go-kit/kit@latest",
    "Data Processing Stack": "github.com/onsi/ginkgo/v2@latest",
}


class GenerateDockerfileRequest(BaseModel):
    """Pydantic model representing the API request for Dockerfile generation."""

    language: str = Field(
        ..., description="Programming language for the Dockerfile (e.g. python, node)"
    )
    dependency_stack: str = Field(
        ..., description="Primary framework or dependency stack (e.g. Django, FastAPI)"
    )
    extra_dependencies: list[str] = Field(
        default_factory=list, description="List of additional packages to install"
    )
    language_version: str = Field(
        ..., description="Version of the programming language (e.g. 3.11)"
    )

    @field_validator("extra_dependencies", mode="before")
    @classmethod
    def sanitize_dependencies(cls, v: list[str]) -> list[str]:
        """Validate extra dependencies against injection attacks."""
        pattern = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._\-\[\]>=<!, ]*$")
        for dep in v:
            if not pattern.match(dep):
                raise ValueError(
                    f"Invalid dependency name: '{dep}'. "
                    "Only alphanumeric characters, hyphens, dots, and version specifiers are allowed."
                )
        return v

    @property
    def extra_dependencies_str(self) -> str:
        """Convert the list of extra dependencies to a space-separated string."""
        return " ".join(self.extra_dependencies)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> "GenerateDockerfileRequest":
        """Create a GenerateDockerfileRequest instance from an API Gateway event."""
        import json
        dict_obj = json.loads(event["body"])
        return cls(**dict_obj["config"])


class DockerfileGenerator(BaseModel):
    """Service class for generating Dockerfile content."""

    config: GenerateDockerfileRequest

    def generate_dockerfile(self) -> str:
        """Generate Dockerfile content using the template and configuration."""
        language = self.config.language.lower()
        if language not in TEMPLATE_REGISTRY:
            raise ValueError(f"Unsupported language: {self.config.language}. Supported: {', '.join(SUPPORTED_LANGUAGES)}")

        start_template, end_template, version_placeholder = TEMPLATE_REGISTRY[language]
        stack_packages = STACK_PACKAGES.get(self.config.dependency_stack, self.config.dependency_stack)
        return (
            start_template.replace(version_placeholder, self.config.language_version)
            .replace("DEPENDENCY_STACK", stack_packages)
            .replace("EXTRA_DEPENDENCIES", self.config.extra_dependencies_str)
            + end_template
        )


def generate_dockerfile_key_name(config: GenerateDockerfileRequest) -> str:
    """Generate a unique S3 key name for the Dockerfile."""
    return (
        f"dockerfile-{config.language}-{config.dependency_stack}-"
        + f"{config.language_version}-{'-'.join(config.extra_dependencies)}.dockerfile"
    )
