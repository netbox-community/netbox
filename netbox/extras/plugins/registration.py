import warnings

from netbox.plugins.registration import *


# TODO: Remove in v4.0
warnings.warn(f"{__name__} is deprecated. Import from netbox.plugins instead.", DeprecationWarning)
