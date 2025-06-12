from django.conf import settings
from django.core.files.storage import storages
from django.db import migrations
from urllib.parse import urlparse

from extras.storage import ScriptFileSystemStorage


def normalize(url):
    parsed_url = urlparse(url)
    if not parsed_url.path.endswith('/'):
        return url + '/'
    return url


def fix_script_paths(apps, schema_editor):
    """
    Fix script paths for scripts that had incorrect path from NB 4.3.
    """
    storage = storages.create_storage(storages.backends["scripts"])
    if not isinstance(storage, ScriptFileSystemStorage):
        return

    ScriptModule = apps.get_model('extras', 'ScriptModule')
    script_root_path = normalize(settings.SCRIPTS_ROOT)
    for script in ScriptModule.objects.all():
        if script.file_path.startswith(script_root_path):
            script.file_path = script.file_path[len(script_root_path):]
            script.save()


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0128_tableconfig'),
    ]

    operations = [
        migrations.RunPython(code=fix_script_paths, reverse_code=migrations.RunPython.noop),
    ]
