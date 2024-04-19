from django_eventstream.channelmanager import DefaultChannelManager
from rest_framework.exceptions import AuthenticationFailed

from .authentication import TokenAuthentication
from .models import Telescope


class TelescopeChannelManager(DefaultChannelManager):

    def get_channels_for_request(self, request, view_kwargs):
        self.request = request
        authentication = TokenAuthentication()
        try:
            request.user, request.auth = authentication.authenticate(request)
        except AuthenticationFailed:
            pass
        return super().get_channels_for_request(request, view_kwargs)

    def can_read_channel(self, _, channel):
        ids = [
            str(id)
            for id in Telescope.objects.all().values_list('id', flat=True)
        ]
        return (
            self.request.user.is_authenticated
            and
            str(channel) in ids
        )
