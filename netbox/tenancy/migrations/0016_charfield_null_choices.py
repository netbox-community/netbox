from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    ContactAssignment = apps.get_model('tenancy', 'ContactAssignment')

    ContactAssignment.objects.filter(priority='').update(priority=None)


class Migration(migrations.Migration):
    dependencies = [
        ('tenancy', '0015_contactassignment_rename_content_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactassignment',
            name='priority',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(code=set_null_values, reverse_code=migrations.RunPython.noop),
    ]
