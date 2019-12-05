from django.db import migrations, models


CIRCUIT_STATUS_CHOICES = (
    (0, 'deprovisioning'),
    (1, 'active'),
    (2, 'planned'),
    (3, 'provisioning'),
    (4, 'offline'),
    (5, 'decommissioned')
)


def circuit_status_to_slug(apps, schema_editor):
    Circuit = apps.get_model('circuits', 'Circuit')
    for id, slug in CIRCUIT_STATUS_CHOICES:
        Circuit.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('circuits', '0015_custom_tag_models'),
    ]

    operations = [

        # Circuit.status
        migrations.AlterField(
            model_name='circuit',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=circuit_status_to_slug
        ),

    ]
