import httpx

from .. import settings


def health_check(timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    response = httpx.get(
        settings.HOME_API_HEALTH_CHECK_URL,
        headers={
            'User-Agent': settings.USER_AGENT,
            'Authorization': f'Token {settings.HOME_AUTHORIZATION_TOKEN}',
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return True


def get_configuration(timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    response = httpx.get(
        settings.DOWNLINK_CONFIGURATION_URL,
        headers={
            'User-Agent': settings.USER_AGENT,
            'Authorization': f'Token {settings.HOME_AUTHORIZATION_TOKEN}',
        },
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def upload_observation(filename, f, timeout=settings.DEFAULT_REQUEST_TIMEOUT):
    response = httpx.post(
        settings.HOME_API_TRANSMIT_URL,
        headers={
            'User-Agent': settings.USER_AGENT,
            'Authorization': f'Token {settings.HOME_AUTHORIZATION_TOKEN}',
            'Content-Encoding': 'gzip',
        },
        data={'name': filename},
        files={'data': f},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
