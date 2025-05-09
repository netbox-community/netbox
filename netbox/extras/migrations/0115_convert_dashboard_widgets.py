from django.db import migrations


def update_dashboard_widgets(apps, schema_editor):
    Dashboard = apps.get_model('extras', 'Dashboard')
    db_alias = schema_editor.connection.alias

    for dashboard in Dashboard.objects.using(db_alias).all():
        for key, widget in dashboard.config.items():
            if models := widget['config'].get('models'):
                models = list(map(lambda x: x.replace('users.netboxgroup', 'users.group'), models))
                models = list(map(lambda x: x.replace('users.netboxuser', 'users.user'), models))
                dashboard.config[key]['config']['models'] = models
        dashboard.save()


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0114_customfield_add_comments'),
    ]

    operations = [
        migrations.RunPython(code=update_dashboard_widgets, reverse_code=migrations.RunPython.noop),
    ]
