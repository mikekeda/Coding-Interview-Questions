import os

import requests

SITE_ENV_PREFIX = "CODING_INTERVIEW_QUESTIONS"


def get_env_var(name: str, default: str = "") -> str:
    """Get all sensitive data from google vm custom metadata."""
    try:
        name = f"{SITE_ENV_PREFIX}_{name}"
        res = os.environ.get(name)
        if res is not None:
            # Check env variable (Jenkins build).
            return res
        else:
            res = requests.get(
                f"http://metadata.google.internal/computeMetadata/v1/instance/attributes/{name}",
                headers={"Metadata-Flavor": "Google"},
            )
            if res.status_code == 200:
                return res.text
    except requests.exceptions.ConnectionError:
        pass

    return default


DEBUG = bool(get_env_var("DEBUG", "True"))

SANIC_CONFIG = {
    "DEBUG": bool(get_env_var("DEBUG", "True")),
    "SOCKET_FILE": get_env_var("SOCKET_FILE", "/temp/site.sock"),
}

EMAIL = get_env_var("EMAIL")
EMAIL_PASSWORD = get_env_var("PASSWORD")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")

DATABASE = "problems.db"

# CELERY STUFF
CELERY_BROKER_URL = "redis://localhost:6379/10"
CELERY_result_backend = "redis://localhost:6379/10"
CELERY_accept_content = ["application/json"]
CELERY_task_serializer = "json"
CELERY_result_serializer = "json"
CELERY_timezone = "UTC"
