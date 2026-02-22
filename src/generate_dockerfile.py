"""Script to generate the dockerfile based on the API parameters"""

import json
import os
from typing import Any, Optional

from dotenv import load_dotenv

from src.generator_core import (
    TEMPLATE_REGISTRY,
    SUPPORTED_LANGUAGES,
    STACK_PACKAGES,
    GenerateDockerfileRequest,
    DockerfileGenerator,
    generate_dockerfile_key_name,
)
from src.s3_helper import upload_to_s3, check_if_file_exists_in_s3

load_dotenv()

# Re-export for backward compatibility
__all__ = [
    "TEMPLATE_REGISTRY",
    "SUPPORTED_LANGUAGES",
    "STACK_PACKAGES",
    "GenerateDockerfileRequest",
    "DockerfileGenerator",
    "generate_dockerfile_key_name",
    "is_running_on_lambda",
    "validate_env_vars",
    "lambda_handler",
    "CORS_HEADERS",
]


def is_running_on_lambda() -> bool:
    """Determine if the code is executing in an AWS Lambda environment."""
    return bool(os.getenv("AWS_LAMBDA_FUNCTION_NAME"))


def validate_env_vars() -> None:
    """Validate required environment variables are present."""
    if not os.getenv("S3_BUCKET"):
        raise ValueError("S3_BUCKET environment variable is not set")
    if not os.getenv("AWS_REGION"):
        raise ValueError("AWS_REGION environment variable is not set")


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

        if not is_running_on_lambda():
            os.makedirs(path, exist_ok=True)
            with open(os.path.join(path, dockerfile_key_name), "w", encoding="utf-8") as f:
                f.write(dockerfile_content)

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
