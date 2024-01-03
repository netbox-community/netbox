from django.db import migrations, models


def update_ui_attrs(apps, schema_editor):
    """
    Replicate legacy ui_visibility values to the new ui_visible and ui_editable fields.
    """
    CustomField = apps.get_model('extras', 'CustomField')

    CustomField.objects.filter(ui_visibility='read-write').update(ui_visible='always', ui_editable='yes')
    CustomField.objects.filter(ui_visibility='read-only').update(ui_visible='always', ui_editable='no')
    CustomField.objects.filter(ui_visibility='hidden').update(ui_visible='hidden', ui_editable='hidden')
    CustomField.objects.filter(ui_visibility='hidden-ifunset').update(ui_visible='if-set', ui_editable='yes')


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0099_cachedvalue_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='ui_editable',
            field=models.CharField(default='yes', max_length=50),
        ),
        migrations.AddField(
            model_name='customfield',
            name='ui_visible',
            field=models.CharField(default='always', max_length=50),
        ),
        migrations.RunPython(
            code=update_ui_attrs,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RemoveField(
            model_name='customfield',
            name='ui_visibility',
        ),
    ]
