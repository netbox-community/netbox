import warnings

from netbox.plugins.registration import *


warnings.warn(f"{__name__} is deprecated. Import from netbox.plugins instead.", DeprecationWarning)
