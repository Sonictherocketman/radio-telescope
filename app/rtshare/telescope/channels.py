from django_eventstream.channelmanager import DefaultChannelManager
from rest_framework.exceptions import AuthenticationFailed

from .authentication import TokenAuthentication
from .models import Telescope


class TelescopeChannelManager(DefaultChannelManager):

    def can_read_channel(self, user, channel):
        print(user)
        ids = [
            str(id)
            for id in Telescope.objects.all().values_list('id', flat=True)
        ]
        return (
            user.is_authenticated
            and
            str(channel) in ids
        )
