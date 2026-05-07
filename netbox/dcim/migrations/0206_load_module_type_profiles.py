import json
from pathlib import Path

from django.db import migrations

DATA_FILES_PATH = Path(__file__).parent / 'initial_data' / 'module_type_profiles'


def load_initial_data(apps, schema_editor):
    """
    Load initial ModuleTypeProfile objects from file.
    """
    ModuleTypeProfile = apps.get_model('dcim', 'ModuleTypeProfile')
    db_alias = schema_editor.connection.alias

    initial_profiles = (
        'cpu',
        'fan',
        'gpu',
        'hard_disk',
        'memory',
        'power_supply',
        'expansion_card'
    )
    profile_objects = []

    for name in initial_profiles:
        file_path = DATA_FILES_PATH / f'{name}.json'
        with file_path.open('r') as f:
            data = json.load(f)
            try:
                profile = ModuleTypeProfile(**data)
                profile_objects.append(profile)
            except Exception as e:
                print(f"Error loading data from {file_path}")
                raise e

    ModuleTypeProfile.objects.using(db_alias).bulk_create(profile_objects)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0205_moduletypeprofile'),
    ]

    operations = [
        migrations.RunPython(load_initial_data),
    ]
