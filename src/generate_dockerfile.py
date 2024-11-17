import json
import os
from typing import Any

from pydantic import BaseModel, Field

from src.docker_templates.python_template import END_OF_TEMPLATE, START_OF_TEMPLATE
from src.s3_helper import upload_to_s3, check_if_file_exists_in_s3
from dotenv import load_dotenv

load_dotenv()


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
        return cls(**event["config"])


class DockerfileGenerator(BaseModel):
    """Service class for generating Dockerfile content and managing file operations.

    Handles the generation of Dockerfile content based on the provided configuration
    and manages saving the generated content to disk or S3.
    """

    config: GenerateDockerfileRequest

    def generate_dockerfile(self) -> str:
        """Generate Dockerfile content using the template and configuration.

        Replaces placeholder values in the template with actual configuration values
        to create a complete Dockerfile.

        Returns:
            str: Complete Dockerfile content with all placeholders replaced
        """
        return (
            START_OF_TEMPLATE.replace("PYTHON_VERSION", self.config.language_version)
            .replace("DEPENDENCY_STACK", self.config.dependency_stack)
            .replace("EXTRA_DEPENDENCIES", self.config.extra_dependencies_str)
            + END_OF_TEMPLATE
        )

    def save_dockerfile(
        self, path: str = "Dockerfile.generated", dir: str = "tmp/"
    ) -> None:
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

        os.makedirs(dir, exist_ok=True)
        with open(os.path.join(dir, path), "w") as f:
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
    return f"dockerfile-{config.language}-{config.dependency_stack}-{config.language_version}-{'-'.join(config.extra_dependencies)}.dockerfile"


def lambda_handler(event: dict[str, Any], context: dict) -> dict:
    """AWS Lambda handler for the Dockerfile generation API endpoint.

    Processes incoming API Gateway requests, generates Dockerfiles,
    and manages S3 storage operations.

    Args:
        event: API Gateway event containing the request data
        context: AWS Lambda context object

    Returns:
        dict: API Gateway response containing status code and response body

    Response format:
        {
            "statusCode": int,
            "body": str (JSON containing message, key, and URL)
        }
    """
    try:
        validate_env_vars()
        config = GenerateDockerfileRequest.from_event(event)
        generator = DockerfileGenerator(config=config)
        dockerfile_content = generator.generate_dockerfile()

        dockerfile_key_name = generate_dockerfile_key_name(config)
        path = "python-images/" if config.language == "python" else ""
        generator.save_dockerfile(path=dockerfile_key_name, dir=path)

        if is_running_on_lambda():
            if check_if_file_exists_in_s3(
                bucket=os.getenv("S3_BUCKET"),
                key=dockerfile_key_name,
                region_name=os.getenv("AWS_REGION"),
            ):
                return {
                    "statusCode": 200,
                    "body": json.dumps(
                        {
                            "message": "Dockerfile already exists",
                            "key": dockerfile_key_name,
                            "url": f"https://{os.getenv('S3_BUCKET')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{path}{dockerfile_key_name}",
                        }
                    ),
                }

            try:
                upload_to_s3(
                    file_path=os.path.join(path, dockerfile_key_name),
                    bucket=os.getenv("S3_BUCKET"),
                    content=dockerfile_content,
                    region_name=os.getenv("AWS_REGION"),
                )
            except Exception as e:
                return {"statusCode": 500, "body": json.dumps({"error": f"Failed to upload Dockerfile to S3, {e}"})}

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "message": "Dockerfile generated successfully",
                    "key": dockerfile_key_name,
                    "url": f"https://{os.getenv('S3_BUCKET')}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{path}{dockerfile_key_name}",
                }
            ),
        }
    except Exception as e:
        return {"statusCode": 400, "body": json.dumps({"error": str(e)})}