from django.db import migrations, models

SITE_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'planned'),
    (4, 'retired'),
)


def site_status_to_slug(apps, schema_editor):
    Site = apps.get_model('dcim', 'Site')
    for id, slug in SITE_STATUS_CHOICES:
        Site.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0077_power_types'),
    ]

    operations = [

        # Site.status
        migrations.AlterField(
            model_name='site',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=site_status_to_slug
        ),

    ]
