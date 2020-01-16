from django.db import migrations, models


VLAN_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
)


def vlan_status_to_slug(apps, schema_editor):
    VLAN = apps.get_model('ipam', 'VLAN')
    for id, slug in VLAN_STATUS_CHOICES:
        VLAN.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('ipam', '0029_3569_ipaddress_fields'),
    ]

    operations = [

        # VLAN.status
        migrations.AlterField(
            model_name='vlan',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=vlan_status_to_slug
        ),

    ]
