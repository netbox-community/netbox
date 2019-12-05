from django.db import migrations, models


CUSTOMFIELD_TYPE_CHOICES = (
    (100, 'text'),
    (200, 'integer'),
    (300, 'boolean'),
    (400, 'date'),
    (500, 'url'),
    (600, 'select')
)


def customfield_type_to_slug(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    for id, slug in CUSTOMFIELD_TYPE_CHOICES:
        CustomField.objects.filter(type=str(id)).update(type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('extras', '0028_remove_topology_maps'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='type',
            field=models.CharField(default='text', max_length=50),
        ),
        migrations.RunPython(
            code=customfield_type_to_slug
        ),
    ]
