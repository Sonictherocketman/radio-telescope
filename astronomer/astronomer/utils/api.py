from subprocess import run
import shlex

import httpx

from .. import settings


def health_check(timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    response = httpx.get(
        settings.HOME_API_HEALTH_CHECK_URL,
        headers={
            'User-Agent': settings.USER_AGENT,
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return True


def upload_observation(
    path,
    timeout=settings.DEFAULT_REQUEST_TIMEOUT,
    host=settings.TRANSMIT_REMOTE_HOST,
    user=settings.TRANSMIT_REMOTE_USER,
    target=settings.TRANSMIT_REMOTE_DIRECTORY,
):
    run(
        shlex.split(f"scp -C '{path}' '{user}@{host}:{target}'"),
        check=True,
        capture_output=True,
        timeout=timeout,
    )
