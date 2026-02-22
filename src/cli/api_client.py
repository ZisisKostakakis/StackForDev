"""HTTP client for the StackForDev public API endpoint."""

import httpx

from src.cli.config import API_URL
from src.generator_core import GenerateDockerfileRequest


def generate_via_api(config: GenerateDockerfileRequest, timeout: float = 15.0) -> dict:
    """POST to the public CLI endpoint and return the response body.

    Returns:
        dict with keys: message, key, dockerfile

    Raises:
        RuntimeError on network/HTTP errors with user-friendly messages.
    """
    payload = {
        "config": {
            "language": config.language,
            "dependency_stack": config.dependency_stack,
            "extra_dependencies": config.extra_dependencies,
            "language_version": config.language_version,
        }
    }

    try:
        response = httpx.post(API_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        raise RuntimeError("Request timed out. Try again or use --local to generate offline.")
    except httpx.ConnectError:
        raise RuntimeError("Could not connect to the API. Check your internet or use --local.")
    except httpx.HTTPStatusError as e:
        body = e.response.text
        raise RuntimeError(f"API returned {e.response.status_code}: {body}")
