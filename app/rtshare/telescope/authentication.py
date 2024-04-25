from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication

from .models import Telescope


class TelescopeUser(AnonymousUser):

    def __init__(self, telescope):
        self.telescope = telescope

    def is_authenticated(self):
        return True


class TelescopeTokenAuthentication(BaseAuthentication):

    prefix = 'device'

    def authenticate(self, request):
        try:
            __, token = (
                request.META.get('HTTP_AUTHORIZATION', '')
                .lower()
                .split(self.prefix)
            )
            token = token.strip()
        except ValueError:
            return None

        if telescope := Telescope.objects.filter(token__key=token).first():
            return (TelescopeUser(telescope=telescope), None)
        else:
            return None
