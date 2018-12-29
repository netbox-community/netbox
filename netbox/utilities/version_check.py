import subprocess
import re

from distutils.version import LooseVersion
from django.conf import settings
from datetime import datetime, timedelta


def check_newer_version():
    def _git_get_latest_version():
        version = '1.0'

        try:
            ps = subprocess.Popen(('git', 'ls-remote', '--tags', settings.CHECK_UPDATES_URL), stdout=subprocess.PIPE)
            output = subprocess.check_output(('tail', '-1'), stdin=ps.stdout)
            ps.wait()
        except FileNotFoundError:
            # Command not found, so git not installed
            settings.CHECK_UPDATES = False
            return LooseVersion(version)

        output = re.search('refs/tags/v(.*)', output.decode())
        if output is not None:
            version = output[1]

        return LooseVersion(version)

    # If check_updates enabled?
    if not settings.CHECK_UPDATES:
        return {}

    if type(settings.HAS_UPDATES.get('latest_version')) is str:
        latest_version = LooseVersion(settings.HAS_UPDATES.get('latest_version'))
    else:
        latest_version = settings.HAS_UPDATES.get('latest_version')

    # If dev, remove it
    cur_version = LooseVersion(settings.VERSION.replace('-dev', ''))

    last_updated = settings.HAS_UPDATES.get('last_updated')

    # Check every 24 hours for updates
    if last_updated is None or ((datetime.utcnow() - last_updated) > timedelta(1)):
        latest_version = _git_get_latest_version()
        settings.HAS_UPDATES = {'latest_version': latest_version, 'last_updated': datetime.utcnow()}

    # Check if this version is older then the newer version
    if cur_version >= latest_version:
        return {}

    return {
        'url': settings.CHECK_UPDATES_URL.replace('.git', ''),
        'latest_version': latest_version.__str__(),
    }
