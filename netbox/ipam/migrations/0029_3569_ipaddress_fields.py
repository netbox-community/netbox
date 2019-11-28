from django.db import migrations, models


IPADDRESS_STATUS_CHOICES = (
    (0, 'container'),
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
)


def ipaddress_status_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    for id, slug in IPADDRESS_STATUS_CHOICES:
        IPAddress.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('ipam', '0028_3569_prefix_fields'),
    ]

    operations = [

        # IPAddress.status
        migrations.AlterField(
            model_name='ipaddress',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=ipaddress_status_to_slug
        ),

    ]
