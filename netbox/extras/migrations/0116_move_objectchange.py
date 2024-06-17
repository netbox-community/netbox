from django.db import migrations


def update_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # Delete the new ContentTypes effected by the new model in the core app
    ContentType.objects.filter(app_label='core', model='objectchange').delete()

    # Update the app labels of the original ContentTypes for extras.ObjectChange to ensure that any
    # foreign key references are preserved
    ContentType.objects.filter(app_label='extras', model='objectchange').update(app_label='core')


def update_dashboard_widgets(apps, schema_editor):
    Dashboard = apps.get_model('extras', 'Dashboard')

    for dashboard in Dashboard.objects.all():
        for key, widget in dashboard.config.items():
            if widget['config'].get('model') == 'extras.objectchange':
                widget['config']['model'] = 'core.objectchange'
            elif models := widget['config'].get('models'):
                models = list(map(lambda x: x.replace('extras.objectchange', 'core.objectchange'), models))
                dashboard.config[key]['config']['models'] = models
        dashboard.save()


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0115_convert_dashboard_widgets'),
        ('core', '0011_move_objectchange'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='ObjectChange',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='ObjectChange',
                    table='core_objectchange',
                ),
            ],
        ),
        migrations.RunPython(
            code=update_content_types,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            code=update_dashboard_widgets,
            reverse_code=migrations.RunPython.noop
        ),
    ]
