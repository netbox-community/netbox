import datetime
import importlib.util
import os
from dataclasses import asdict, dataclass, field

import yaml
from django.core.exceptions import ImproperlyConfigured

from utilities.datetime import datetime_from_timestamp

RELEASE_PATH = 'release.yaml'
LOCAL_RELEASE_PATH = 'local/release.yaml'


def _find_release_base_path():
    """
    Return the directory containing release.yaml.

    In a source checkout, release.yaml lives under the NetBox application root
    beside manage.py. In a wheel install, release.yaml is bundled under the
    installed netbox package's _data directory.
    """
    checkout_base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if os.path.isfile(os.path.join(checkout_base_path, RELEASE_PATH)):
        return checkout_base_path

    spec = importlib.util.find_spec('netbox')  # pragma: no cover
    locations = spec.submodule_search_locations if spec is not None else ()  # pragma: no cover
    for location in locations or ():  # pragma: no cover
        bundled_base_path = os.path.join(location, '_data')
        if os.path.isfile(os.path.join(bundled_base_path, RELEASE_PATH)):
            return bundled_base_path

    raise ImproperlyConfigured(f"Unable to locate {RELEASE_PATH} for this NetBox installation.")  # pragma: no cover


@dataclass
class FeatureSet:
    """
    A map of all available NetBox features.
    """
    # Commercial support is provided by NetBox Labs
    commercial: bool = False

    # Live help center is enabled
    help_center: bool = False


@dataclass
class ReleaseInfo:
    version: str
    edition: str
    published: datetime.date | None = None
    designation: str | None = None
    build: str | None = None
    features: FeatureSet = field(default_factory=FeatureSet)

    @property
    def full_version(self):
        output = self.version
        if self.designation:
            output = f"{output}-{self.designation}"
        if self.build:
            output = f"{output}-{self.build}"
        return output

    @property
    def name(self):
        return f"NetBox {self.edition} v{self.full_version}"

    def asdict(self):
        return asdict(self)


def load_release_data():
    """
    Load any locally-defined release attributes and return a ReleaseInfo instance.
    """
    base_path = _find_release_base_path()

    # Load canonical release attributes
    with open(os.path.join(base_path, RELEASE_PATH)) as release_file:
        data = yaml.safe_load(release_file)

    # Overlay any local release date (if defined)
    try:
        with open(os.path.join(base_path, LOCAL_RELEASE_PATH)) as release_file:
            local_data = yaml.safe_load(release_file)
    except FileNotFoundError:
        local_data = {}
    if local_data is not None:
        if type(local_data) is not dict:
            raise ImproperlyConfigured(
                f"{LOCAL_RELEASE_PATH}: Local release data must be defined as a dictionary."
            )
        data.update(local_data)

    # Convert the published date to a date object
    if 'published' in data:
        data['published'] = datetime_from_timestamp(data['published'])

    return ReleaseInfo(**data)
