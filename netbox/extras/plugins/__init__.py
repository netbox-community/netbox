from .navigation import *
from .registration import *
from .templates import *
from .utils import *
from netbox.plugins import PluginConfig


# TODO: Remove in v4.0
warnings.warn(f"{__name__} is deprecated. Import from netbox.plugins instead.", DeprecationWarning)
