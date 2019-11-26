from django.db import migrations, models


POWERFEED_TYPE_CHOICES = (
    (1, 'primary'),
    (2, 'redundant'),
)


def powerfeed_type_to_slug(apps, schema_editor):
    PowerFeed = apps.get_model('dcim', 'PowerFeed')
    for id, slug in POWERFEED_TYPE_CHOICES:
        PowerFeed.objects.filter(type=id).update(type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0083_3569_cable_fields'),
    ]

    operations = [

        # Cable.type
        migrations.AlterField(
            model_name='powerfeed',
            name='type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.RunPython(
            code=powerfeed_type_to_slug
        ),

    ]
