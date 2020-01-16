import django.core.validators
from django.db import migrations, models
import django.db.models.expressions

PREFIX_STATUS_CHOICES = (
    (0, 'container'),
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
)

IPADDRESS_STATUS_CHOICES = (
    (0, 'container'),
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
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

VLAN_STATUS_CHOICES = (
    (1, 'active'),
    (2, 'reserved'),
    (3, 'deprecated'),
)

SERVICE_PROTOCOL_CHOICES = (
    (6, 'tcp'),
    (17, 'udp'),
)


def prefix_status_to_slug(apps, schema_editor):
    Prefix = apps.get_model('ipam', 'Prefix')
    for id, slug in PREFIX_STATUS_CHOICES:
        Prefix.objects.filter(status=str(id)).update(status=slug)


def ipaddress_status_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    for id, slug in IPADDRESS_STATUS_CHOICES:
        IPAddress.objects.filter(status=str(id)).update(status=slug)


def ipaddress_role_to_slug(apps, schema_editor):
    IPAddress = apps.get_model('ipam', 'IPAddress')
    for id, slug in IPADDRESS_ROLE_CHOICES:
        IPAddress.objects.filter(role=str(id)).update(role=slug)


def vlan_status_to_slug(apps, schema_editor):
    VLAN = apps.get_model('ipam', 'VLAN')
    for id, slug in VLAN_STATUS_CHOICES:
        VLAN.objects.filter(status=str(id)).update(status=slug)


def service_protocol_to_slug(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    for id, slug in SERVICE_PROTOCOL_CHOICES:
        Service.objects.filter(protocol=str(id)).update(protocol=slug)


class Migration(migrations.Migration):

    replaces = [('ipam', '0026_prefix_ordering_vrf_nulls_first'), ('ipam', '0027_ipaddress_add_dns_name'), ('ipam', '0028_3569_prefix_fields'), ('ipam', '0029_3569_ipaddress_fields'), ('ipam', '0030_3569_vlan_fields'), ('ipam', '0031_3569_service_fields'), ('ipam', '0032_role_description')]

    dependencies = [
        ('ipam', '0025_custom_tag_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='prefix',
            options={'ordering': [django.db.models.expressions.OrderBy(django.db.models.expressions.F('vrf'), nulls_first=True), 'family', 'prefix'], 'verbose_name_plural': 'prefixes'},
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='dns_name',
            field=models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator(code='invalid', message='Only alphanumeric characters, hyphens, periods, and underscores are allowed in DNS names', regex='^[0-9A-Za-z._-]+$')]),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=prefix_status_to_slug,
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=ipaddress_status_to_slug,
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='role',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(
            code=ipaddress_role_to_slug,
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='role',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=vlan_status_to_slug,
        ),
        migrations.AlterField(
            model_name='service',
            name='protocol',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=service_protocol_to_slug,
        ),
        migrations.AddField(
            model_name='role',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
