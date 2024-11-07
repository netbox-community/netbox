import inspect
import os
from importlib.machinery import SourceFileLoader

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

#
# Note: This has a couple dependencies on the codebase if doing future modifications:
# There are imports from extras.scripts and extras.reports as well as expecting
# settings.SCRIPTS_ROOT and settings.REPORTS_ROOT to be in settings
#

ROOT_PATHS = {
    'scripts': settings.SCRIPTS_ROOT,
    'reports': settings.REPORTS_ROOT,
}


def get_full_path(scriptmodule):
    """
    Return the full path to a ScriptModule's file on disk.
    """
    root_path = ROOT_PATHS[scriptmodule.file_root]
    return os.path.join(root_path, scriptmodule.file_path)


def get_python_name(scriptmodule):
    """
    Return the Python name of a ScriptModule's file on disk.
    """
    filename = os.path.split(scriptmodule.file_path)[0]
    return os.path.splitext(filename)[0]


def is_script(obj):
    """
    Returns True if the passed Python object is a Script or Report.
    """
    from extras.scripts import Script
    from extras.reports import Report

    try:
        if issubclass(obj, Report) and obj != Report:
            return True
        if issubclass(obj, Script) and obj != Script:
            return True
    except TypeError:
        pass
    return False


def get_module_scripts(scriptmodule):
    """
    Return a dictionary mapping of name and script class inside the passed ScriptModule.
    """
    def get_name(cls):
        # For child objects in submodules use the full import path w/o the root module as the name
        return cls.full_name.split(".", maxsplit=1)[1]

    loader = SourceFileLoader(get_python_name(scriptmodule), get_full_path(scriptmodule))
    try:
        module = loader.load_module()
    except FileNotFoundError:
        return {}

    scripts = {}
    ordered = getattr(module, 'script_order', [])

    for cls in ordered:
        scripts[get_name(cls)] = cls
    for name, cls in inspect.getmembers(module, is_script):
        if cls not in ordered:
            scripts[get_name(cls)] = cls

    return scripts


def update_scripts(apps, schema_editor):
    """
    Create a new Script object for each script inside each existing ScriptModule, and update any related jobs to
    reference the new Script object.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Script = apps.get_model('extras', 'Script')
    ScriptModule = apps.get_model('extras', 'ScriptModule')
    ReportModule = apps.get_model('extras', 'ReportModule')
    Job = apps.get_model('core', 'Job')

    script_ct = ContentType.objects.get_for_model(Script, for_concrete_model=False)
    scriptmodule_ct = ContentType.objects.get_for_model(ScriptModule, for_concrete_model=False)
    reportmodule_ct = ContentType.objects.get_for_model(ReportModule, for_concrete_model=False)

    for module in ScriptModule.objects.all():
        for script_name in get_module_scripts(module):
            script = Script.objects.create(
                name=script_name,
                module=module,
            )

            # Update all Jobs associated with this ScriptModule & script name to point to the new Script object
            Job.objects.filter(
                object_type_id=scriptmodule_ct.id,
                object_id=module.pk,
                name=script_name
            ).update(object_type_id=script_ct.id, object_id=script.pk)
            # Update all Jobs associated with this ScriptModule & script name to point to the new Script object
            Job.objects.filter(
                object_type_id=reportmodule_ct.id,
                object_id=module.pk,
                name=script_name
            ).update(object_type_id=script_ct.id, object_id=script.pk)


def update_event_rules(apps, schema_editor):
    """
    Update any existing EventRules for scripts. Change action_object_type from ScriptModule to Script, and populate
    the ID of the related Script object.
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Script = apps.get_model('extras', 'Script')
    ScriptModule = apps.get_model('extras', 'ScriptModule')
    EventRule = apps.get_model('extras', 'EventRule')

    script_ct = ContentType.objects.get_for_model(Script)
    scriptmodule_ct = ContentType.objects.get_for_model(ScriptModule)

    for eventrule in EventRule.objects.filter(action_object_type=scriptmodule_ct):
        name = eventrule.action_parameters.get('script_name')
        obj, __ = Script.objects.get_or_create(
            module_id=eventrule.action_object_id,
            name=name,
            defaults={'is_executable': False}
        )
        EventRule.objects.filter(pk=eventrule.pk).update(action_object_type=script_ct, action_object_id=obj.id)


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0108_convert_reports_to_scripts'),
    ]

    operations = [
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(editable=False, max_length=79)),
                ('module', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='scripts', to='extras.scriptmodule')),
                ('is_executable', models.BooleanField(editable=False, default=True))
            ],
            options={
                'ordering': ('module', 'name'),
            },
        ),
        migrations.AddConstraint(
            model_name='script',
            constraint=models.UniqueConstraint(fields=('name', 'module'), name='extras_script_unique_name_module'),
        ),
        migrations.RunPython(
            code=update_scripts,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=update_event_rules,
            reverse_code=migrations.RunPython.noop
        ),
    ]
