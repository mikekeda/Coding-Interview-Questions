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
