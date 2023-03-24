import os
import pkgutil

from django.conf import settings
from django.db import migrations, models
import extras.models.models


def create_files(cls, root_name, root_path):

    path_tree = [
        path for path, _, _ in os.walk(root_path)
        if os.path.basename(path)[0] not in ('_', '.')
    ]

    modules = list(pkgutil.iter_modules(path_tree))
    filenames = []
    for importer, module_name, is_pkg in modules:
        if is_pkg:
            continue
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
