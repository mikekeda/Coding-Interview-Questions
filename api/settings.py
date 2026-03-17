import os

import requests

SITE_ENV_PREFIX = "CODING"


def get_env_var(name: str, default: str = "") -> str:
    """Get sensitive data from env vars, Oracle Cloud IMDS, or Google Cloud metadata."""
    name = f"{SITE_ENV_PREFIX}_{name}"

    env_var = os.environ.get(name)
    if env_var is not None:
        return env_var

    # Try Oracle Cloud IMDS (only reachable on OCI instances)
    try:
        res = requests.get(
            f"http://169.254.169.254/opc/v2/instance/metadata/{name}",
            headers={"Authorization": "Bearer Oracle"},
            timeout=2,
        )
        if res.status_code == 200:
            return res.text.strip()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass

    # Try Google Cloud metadata (only reachable on GCP instances)
    try:
        res = requests.get(
            f"http://metadata.google.internal/computeMetadata/v1/instance/attributes/{name}",
            headers={"Metadata-Flavor": "Google"},
            timeout=2,
        )
        if res.status_code == 200:
            return res.text.strip()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        pass

    return default


DEBUG = bool(get_env_var("DEBUG", "True"))

SANIC_CONFIG = {
    "DEBUG": bool(get_env_var("DEBUG", "True")),
    "SOCKET_FILE": get_env_var("SOCKET_FILE", "/temp/site.sock"),
    "DATABASE": "problems.db",
    "DOMAIN": get_env_var("DOMAIN", "http://localhost:3000"),
    "DB_USER": get_env_var("DB_USER", "coding_admin"),
    "DB_PASSWORD": get_env_var("DB_PASSWORD", ")e6`M94.F3.lE'i0}t-H"),
    "DB_HOST": get_env_var("DB_HOST", "127.0.0.1"),
    "DB_DATABASE": get_env_var("DB_NAME", "coding"),
}

EMAIL = get_env_var("EMAIL")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
OPENAI_API_KEY = get_env_var("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-5.4-mini"  # "gpt-4.1-mini"

# CELERY STUFF
CELERY_BROKER_URL = "redis://localhost:6379/10"
CELERY_result_backend = "redis://localhost:6379/10"
CELERY_accept_content = ["application/json"]
CELERY_task_serializer = "json"
CELERY_result_serializer = "json"
CELERY_timezone = "UTC"
