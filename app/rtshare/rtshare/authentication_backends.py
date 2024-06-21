import logging

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


User = get_user_model()


class TokenAuthenticationBackend(BaseBackend):

    def authenticate(self, request, token=None, **kwargs):
        logger.debug('Attempting to authenticate request via token auth...')
        if not request:
            return None

        if authorization := request.META.get('HTTP_AUTHORIZATION'):
            try:
                _, key = authorization.split(' ')
                token = Token.objects.get(key=key)
                return self.get_user(token.user_id)
            except Token.DoesNotExist:
                logger.warning('Provided token with key does not exist.')
            except ValueError:
                logger.warning('Invalid token value')
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
