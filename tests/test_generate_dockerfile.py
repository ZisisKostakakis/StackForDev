from src.generate_dockerfile import lambda_handler
import json
import shutil


def test_lambda_handler():
    test_event = {
        "config": {
            "language": "python",
            "dependency_stack": "Django",
            "extra_dependencies": ["pandas", "numpy"],
            "language_version": "3.11",
        }
    }
    result = lambda_handler(event=test_event, context={})

    assert result["statusCode"] == 200
    response_body = json.loads(result["body"])
    assert "message" in response_body
    assert "key" in response_body
    assert "url" in response_body
    assert response_body["key"].startswith("dockerfile-python-Django-3.11")

    shutil.rmtree("python-images/")
