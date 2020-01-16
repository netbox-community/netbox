from django.db import migrations, models


SERVICE_PROTOCOL_CHOICES = (
    (6, 'tcp'),
    (17, 'udp'),
)


def service_protocol_to_slug(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    for id, slug in SERVICE_PROTOCOL_CHOICES:
        Service.objects.filter(protocol=str(id)).update(protocol=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('ipam', '0030_3569_vlan_fields'),
    ]

    operations = [

        # Service.protocol
        migrations.AlterField(
            model_name='service',
            name='protocol',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=service_protocol_to_slug
        ),

    ]
