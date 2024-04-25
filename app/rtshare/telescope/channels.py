from django_eventstream.channelmanager import DefaultChannelManager

from .authentication import TelescopeUser
from .models import Telescope


class TelescopeChannelManager(DefaultChannelManager):

    def can_read_channel(self, user, channel):
        # Unauthenticated users can't read any channels.

        if not (user and user.is_authenticated):
            return False

        # Telescope Users can only read their own channel.

        if isinstance(user, TelescopeUser):
            return channel == user.telescope.public_id

        # Normal authenticated users can read any telescope or their own channel.
        telescope_channels = [
            telescope.public_id
            for telescope in Telescope.objects.filter(status=Telescope.Status.ACTIVE)
        ]
        user_channel = f'U-{user.id}'
        all_channels = [*telescope_channels, user_channel]
        return channel in all_channels
