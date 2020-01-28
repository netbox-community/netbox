from django.db import migrations, models


IPADDRESS_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
    (5, 'dhcp'),
)

IPADDRESS_ROLE_CHOICES = (
    (10, 'loopback'),
    (20, 'secondary'),
    (30, 'anycast'),
    (40, 'vip'),
    (41, 'vrrp'),
    (42, 'hsrp'),
    (43, 'glbp'),
    (44, 'carp'),
)


def ipaddress_status_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    for id, slug in IPADDRESS_STATUS_CHOICES:
        IPAddress.objects.filter(status=str(id)).update(status=slug)


def ipaddress_role_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    for id, slug in IPADDRESS_ROLE_CHOICES:
        IPAddress.objects.filter(role=str(id)).update(role=slug)


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

        # IPAddress.role
        migrations.AlterField(
            model_name='ipaddress',
            name='role',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=ipaddress_role_to_slug
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='role',
            field=models.CharField(blank=True, max_length=50),
        ),

    ]
