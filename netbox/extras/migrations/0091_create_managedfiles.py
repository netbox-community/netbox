import os
import pkgutil

from django.conf import settings
from django.db import migrations, models
import extras.models.mixins


def create_files(cls, root_name, root_path):

    modules = list(pkgutil.iter_modules([root_path]))
    filenames = []
    for importer, module_name, ispkg in modules:
        try:
            module = importer.find_module(module_name).load_module(module_name)
            rel_path = os.path.relpath(module.__file__, root_path)
            filenames.append(rel_path)
        except ImportError:
            pass

    managed_files = [
        cls(file_root=root_name, file_path=filename)
        for filename in filenames
    ]
    cls.objects.bulk_create(managed_files)


def replicate_scripts(apps, schema_editor):
    ScriptModule = apps.get_model('extras', 'ScriptModule')
    create_files(ScriptModule, 'scripts', settings.SCRIPTS_ROOT)


def replicate_reports(apps, schema_editor):
    ReportModule = apps.get_model('extras', 'ReportModule')
    create_files(ReportModule, 'reports', settings.REPORTS_ROOT)


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
            bases=(extras.models.mixins.PythonModuleMixin, 'core.managedfile', models.Model),
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
            bases=(extras.models.mixins.PythonModuleMixin, 'core.managedfile', models.Model),
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
