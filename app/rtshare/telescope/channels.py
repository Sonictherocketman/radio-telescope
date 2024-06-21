from django_eventstream.channelmanager import DefaultChannelManager

from .models import Telescope


class TelescopeChannelManager(DefaultChannelManager):

    def can_read_channel(self, user, channel):
        # Unauthenticated users can't read any channels.

        print(user)
        if not (user and user.is_authenticated):
            print('unauth')
            return False

        # Authenticated users can read:
        # the channel of any telescope in a group they are a part of
        # OR their own channel.
        telescope_channels = [
            telescope.public_id
            for telescope in Telescope.objects.filter(groups__in=user.groups.all())
        ]
        user_channel = f'U-{user.id}'
        all_channels = [*telescope_channels, user_channel]
        return channel in all_channels
