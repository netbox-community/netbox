import datetime
import os
import yaml
from dataclasses import dataclass
from typing import Union

from django.core.exceptions import ImproperlyConfigured

RELEASE_PATH = 'release.yaml'
LOCAL_RELEASE_PATH = 'local/release.yaml'


@dataclass
class ReleaseInfo:
    version: str
    edition: str = 'Community'
    published: Union[datetime.date, None] = None
    designation: Union[str, None] = None

    @property
    def full_version(self):
        if self.designation:
            return f"{self.version}-{self.designation}"
        return self.version

    @property
    def name(self):
        return f"NetBox {self.edition} v{self.full_version}"


def load_release_data():
    """
    Load any locally-defined release attributes and return a ReleaseInfo instance.
    """
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Load canonical release attributes
    with open(os.path.join(base_path, RELEASE_PATH), 'r') as release_file:
        data = yaml.safe_load(release_file)

    # Overlay any local release date (if defined)
    try:
        with open(os.path.join(base_path, LOCAL_RELEASE_PATH), 'r') as release_file:
            local_data = yaml.safe_load(release_file)
    except FileNotFoundError:
        local_data = {}
    if type(local_data) is not dict:
        raise ImproperlyConfigured(
            f"{LOCAL_RELEASE_PATH}: Local release data must be defined as a dictionary."
        )
    data.update(local_data)

    # Convert the published date to a date object
    if 'published' in data:
        data['published'] = datetime.date.fromisoformat(data['published'])

    return ReleaseInfo(**data)
