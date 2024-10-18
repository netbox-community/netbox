from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    VMInterface = apps.get_model('virtualization', 'VMInterface')

    VMInterface.objects.filter(mode='').update(mode=None)


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0040_convert_disk_size'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vminterface',
            name='mode',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(
            code=set_null_values,
            reverse_code=migrations.RunPython.noop
        ),
    ]
