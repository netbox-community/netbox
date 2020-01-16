import sys

import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import dcim.fields

CONNECTION_STATUS_CONNECTED = True

CIRCUIT_STATUS_CHOICES = (
    (0, 'deprovisioning'),
    (1, 'active'),
    (2, 'planned'),
    (3, 'provisioning'),
    (4, 'offline'),
    (5, 'decommissioned')
)


def circuit_terminations_to_cables(apps, schema_editor):
    """
    Copy all existing CircuitTermination Interface associations as Cables
    """
    ContentType = apps.get_model('contenttypes', 'ContentType')
    CircuitTermination = apps.get_model('circuits', 'CircuitTermination')
    Interface = apps.get_model('dcim', 'Interface')
    Cable = apps.get_model('dcim', 'Cable')

    # Load content types
    circuittermination_type = ContentType.objects.get_for_model(CircuitTermination)
    interface_type = ContentType.objects.get_for_model(Interface)

    # Create a new Cable instance from each console connection
    if 'test' not in sys.argv:
        print("\n    Adding circuit terminations... ", end='', flush=True)
    for circuittermination in CircuitTermination.objects.filter(interface__isnull=False):

        # Create the new Cable
        cable = Cable.objects.create(
            termination_a_type=circuittermination_type,
            termination_a_id=circuittermination.id,
            termination_b_type=interface_type,
            termination_b_id=circuittermination.interface_id,
            status=CONNECTION_STATUS_CONNECTED
        )

        # Cache the Cable on its two termination points
        CircuitTermination.objects.filter(pk=circuittermination.pk).update(
            cable=cable,
            connected_endpoint=circuittermination.interface,
            connection_status=CONNECTION_STATUS_CONNECTED
        )
        # Cache the connected Cable on the Interface
        Interface.objects.filter(pk=circuittermination.interface_id).update(
            cable=cable,
            _connected_circuittermination=circuittermination,
            connection_status=CONNECTION_STATUS_CONNECTED
        )

    cable_count = Cable.objects.filter(termination_a_type=circuittermination_type).count()
    if 'test' not in sys.argv:
        print("{} cables created".format(cable_count))


def circuit_status_to_slug(apps, schema_editor):
    Circuit = apps.get_model('circuits', 'Circuit')
    for id, slug in CIRCUIT_STATUS_CHOICES:
        Circuit.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):

    replaces = [('circuits', '0007_circuit_add_description'), ('circuits', '0008_circuittermination_interface_protect_on_delete'), ('circuits', '0009_unicode_literals'), ('circuits', '0010_circuit_status'), ('circuits', '0011_tags'), ('circuits', '0012_change_logging'), ('circuits', '0013_cables'), ('circuits', '0014_circuittermination_description'), ('circuits', '0015_custom_tag_models'), ('circuits', '0016_3569_circuit_fields'), ('circuits', '0017_circuittype_description')]

    dependencies = [
        ('circuits', '0006_terminations'),
        ('extras', '0019_tag_taggeditem'),
        ('taggit', '0002_auto_20150616_2121'),
        ('dcim', '0066_cables'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuit',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='interface',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_termination', to='dcim.Interface'),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='cid',
            field=models.CharField(max_length=50, verbose_name='Circuit ID'),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='commit_rate',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Commit rate (Kbps)'),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='install_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date installed'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='port_speed',
            field=models.PositiveIntegerField(verbose_name='Port speed (Kbps)'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='pp_info',
            field=models.CharField(blank=True, max_length=100, verbose_name='Patch panel/port(s)'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='term_side',
            field=models.CharField(choices=[('A', 'A'), ('Z', 'Z')], max_length=1, verbose_name='Termination'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='upstream_speed',
            field=models.PositiveIntegerField(blank=True, help_text='Upstream speed, if different from port speed', null=True, verbose_name='Upstream speed (Kbps)'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='xconnect_id',
            field=models.CharField(blank=True, max_length=50, verbose_name='Cross-connect ID'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='account',
            field=models.CharField(blank=True, max_length=30, verbose_name='Account number'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='admin_contact',
            field=models.TextField(blank=True, verbose_name='Admin contact'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='asn',
            field=dcim.fields.ASNField(blank=True, null=True, verbose_name='ASN'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='noc_contact',
            field=models.TextField(blank=True, verbose_name='NOC contact'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='portal_url',
            field=models.URLField(blank=True, verbose_name='Portal'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[[2, 'Planned'], [3, 'Provisioning'], [1, 'Active'], [4, 'Offline'], [0, 'Deprovisioning'], [5, 'Decommissioned']], default=1),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='circuittype',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittype',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Interface'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable'),
        ),
        migrations.RunPython(
            code=circuit_terminations_to_cables,
        ),
        migrations.RemoveField(
            model_name='circuittermination',
            name='interface',
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=circuit_status_to_slug,
        ),
        migrations.AddField(
            model_name='circuittype',
            name='description',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
