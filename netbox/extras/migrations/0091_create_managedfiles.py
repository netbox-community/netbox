import pkgutil

from django.conf import settings
from django.db import migrations, models
import extras.models.models


def create_files(cls, root_name, path):

    modules = list(pkgutil.iter_modules([path]))
    filenames = [f'{m.name}.py' for m in modules]

    managed_files = [
        cls(
            file_root=root_name,
            file_path=filename
        ) for filename in filenames
    ]
    cls.objects.bulk_create(managed_files)


def replicate_scripts(apps, schema_editor):
    ManagedFile = apps.get_model('core', 'ManagedFile')
    create_files(ManagedFile, 'scripts', settings.SCRIPTS_ROOT)


def replicate_reports(apps, schema_editor):
    ManagedFile = apps.get_model('core', 'ManagedFile')
    create_files(ManagedFile, 'reports', settings.REPORTS_ROOT)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_managedfile'),
        ('extras', '0090_objectchange_index_request_id'),
    ]

    operations = [
        # Create proxy models
        migrations.CreateModel(
            name='ReportModule',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(extras.models.models.PythonModuleMixin, 'core.managedfile', models.Model),
        ),
        migrations.CreateModel(
            name='ScriptModule',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(extras.models.models.PythonModuleMixin, 'core.managedfile', models.Model),
        ),

        # Instantiate ManagedFiles to represent scripts & reports
        migrations.RunPython(
            code=replicate_scripts,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=replicate_reports,
            reverse_code=migrations.RunPython.noop
        ),
    ]
