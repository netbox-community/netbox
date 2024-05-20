from decimal import Decimal
from django.utils.translation import gettext_lazy as _

from .choices import WirelessChannelChoices

__all__ = (
    'get_channel_attr',
)


def get_channel_attr(channel, attr):
    """
    Return the specified attribute of a given WirelessChannelChoices value.
    """
    if channel not in WirelessChannelChoices.values():
        raise ValueError(_("Invalid channel value: {channel}").format(channel=channel))

    channel_values = channel.split('-')
    attrs = {
        'band': channel_values[0],
        'id': int(channel_values[1]),
        'frequency': Decimal(channel_values[2]),
        'width': Decimal(channel_values[3]),
    }
    if attr not in attrs:
        raise ValueError(_("Invalid channel attribute: {name}").format(name=attr))

    return attrs[attr]
