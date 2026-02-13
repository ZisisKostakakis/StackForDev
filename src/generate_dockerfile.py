"""Script to generate the dockerfile based on the API parameters"""

import json
import os
import re
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator

from src.docker_templates import python_template, javascript_template, go_template
from src.s3_helper import upload_to_s3, check_if_file_exists_in_s3
from dotenv import load_dotenv

load_dotenv()

TEMPLATE_REGISTRY: dict[str, tuple] = {
    "python": (python_template.START_OF_TEMPLATE, python_template.END_OF_TEMPLATE, "PYTHON_VERSION"),
    "javascript": (javascript_template.START_OF_TEMPLATE, javascript_template.END_OF_TEMPLATE, "NODE_VERSION"),
    "go": (go_template.START_OF_TEMPLATE, go_template.END_OF_TEMPLATE, "GO_VERSION"),
}

SUPPORTED_LANGUAGES = set(TEMPLATE_REGISTRY.keys())


def is_running_on_lambda() -> bool:
    """Determine if the code is executing in an AWS Lambda environment.

    Checks for the presence of the AWS_LAMBDA_FUNCTION_NAME environment variable,
    which is automatically set in Lambda execution environments.

    Returns:
        bool: True if running in AWS Lambda, False if running locally
    """
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


class GenerateDockerfileRequest(BaseModel):
    """Pydantic model representing the API request for Dockerfile generation.

    This model validates and structures the incoming API request data,
    ensuring all required fields are present and correctly formatted.
    """

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
        """Convert the list of extra dependencies to a space-separated string.

        Returns:
            str: Space-separated string of extra dependencies
        """
        return " ".join(self.extra_dependencies)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> "GenerateDockerfileRequest":
        """Create a GenerateDockerfileRequest instance from an API Gateway event.

        Args:
            event: Raw API Gateway event dictionary containing the request data

        Returns:
            GenerateDockerfileRequest: Validated request model instance

        Raises:
            ValidationError: If the event data doesn't match the expected schema
        """
        dict_obj = json.loads(event["body"])
        return cls(**dict_obj["config"])


class DockerfileGenerator(BaseModel):
    """Service class for generating Dockerfile content and managing file operations.

    Handles the generation of Dockerfile content based on the provided configuration
    and manages saving the generated content to disk or S3.
    """

    config: GenerateDockerfileRequest

    def generate_dockerfile(self) -> str:
        """Generate Dockerfile content using the template and configuration."""
        language = self.config.language.lower()
        if language not in TEMPLATE_REGISTRY:
            raise ValueError(f"Unsupported language: {self.config.language}. Supported: {', '.join(SUPPORTED_LANGUAGES)}")

        start_template, end_template, version_placeholder = TEMPLATE_REGISTRY[language]
        return (
            start_template.replace(version_placeholder, self.config.language_version)
            .replace("DEPENDENCY_STACK", self.config.dependency_stack)
            .replace("EXTRA_DEPENDENCIES", self.config.extra_dependencies_str)
            + end_template
        )

    def save_dockerfile(self, path: str = "Dockerfile.generated", directory: str = "tmp/") -> None:
        """Save the generated Dockerfile to the local filesystem.

        Note: This operation is skipped when running on Lambda.

        Args:
            path: Name of the Dockerfile to create
            dir: Directory where the Dockerfile should be saved

        Raises:
            OSError: If there are filesystem permission issues or other IO errors
        """
        if is_running_on_lambda():
            return

        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, path), "w", encoding="utf-8") as f:
            f.write(self.generate_dockerfile())


def validate_env_vars() -> None:
    """Validate required environment variables are present.

    Checks for the presence of essential environment variables needed
    for S3 operations.

    Raises:
        ValueError: If any required environment variable is missing
    """
    if not os.getenv("S3_BUCKET"):
        raise ValueError("S3_BUCKET environment variable is not set")
    if not os.getenv("AWS_REGION"):
        raise ValueError("AWS_REGION environment variable is not set")


def generate_dockerfile_key_name(config: GenerateDockerfileRequest) -> str:
    """Generate a unique S3 key name for the Dockerfile.

    Creates a standardized filename based on the configuration parameters.

    Args:
        config: The validated request configuration

    Returns:
        str: Formatted key name for S3 storage
    """
    return (
        f"dockerfile-{config.language}-{config.dependency_stack}-"
        + f"{config.language_version}-{'-'.join(config.extra_dependencies)}.dockerfile"
    )


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
}


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": CORS_HEADERS,
        "body": json.dumps(body),
    }


def lambda_handler(event: dict[str, Any], context: Optional[dict] = None) -> dict:
    """AWS Lambda handler for the Dockerfile generation API endpoint."""
    try:
        validate_env_vars()
        config = GenerateDockerfileRequest.from_event(event)
        generator = DockerfileGenerator(config=config)
        dockerfile_content = generator.generate_dockerfile()

        dockerfile_key_name = generate_dockerfile_key_name(config)
        path = f"{config.language.lower()}-images/"
        generator.save_dockerfile(path=dockerfile_key_name, directory=path)

        aws_region = os.getenv("AWS_REGION")
        bucket = os.getenv("S3_BUCKET")

        if is_running_on_lambda():
            s3_key = os.path.join(path, dockerfile_key_name)
            if not check_if_file_exists_in_s3(
                bucket=bucket,
                key=s3_key,
                region_name=aws_region,
            ):
                try:
                    upload_to_s3(
                        file_path=s3_key,
                        bucket=bucket,
                        content=dockerfile_content,
                        region_name=aws_region,
                    )
                except Exception as e:
                    return _response(500, {"error": f"Failed to upload Dockerfile to S3, {e}"})

        return _response(200, {
            "message": "Dockerfile generated successfully",
            "key": dockerfile_key_name,
            "dockerfile": dockerfile_content,
        })
    except Exception as e:
        return _response(400, {"error": str(e)})
