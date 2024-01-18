import dcim.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.functions.text
import taggit.managers
import utilities.fields
import utilities.json
import utilities.ordering
import utilities.query_functions
import utilities.tracking


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('ipam', '0001_initial'),
        ('dcim', '0002_squashed'),
        ('tenancy', '0001_initial'),
    ]

    replaces = [
        # Squashed for v3.0
        ('virtualization', '0001_virtualization'),
        ('virtualization', '0002_virtualmachine_add_status'),
        ('virtualization', '0003_cluster_add_site'),
        ('virtualization', '0004_virtualmachine_add_role'),
        ('virtualization', '0005_django2'),
        ('virtualization', '0006_tags'),
        ('virtualization', '0007_change_logging'),
        ('virtualization', '0008_virtualmachine_local_context_data'),
        ('virtualization', '0009_custom_tag_models'),
        ('virtualization', '0010_cluster_add_tenant'),
        ('virtualization', '0011_3569_virtualmachine_fields'),
        ('virtualization', '0012_vm_name_nonunique'),
        ('virtualization', '0013_deterministic_ordering'),
        ('virtualization', '0014_standardize_description'),
        ('virtualization', '0015_vminterface'),
        ('virtualization', '0016_replicate_interfaces'),
        ('virtualization', '0017_update_jsonfield'),
        ('virtualization', '0018_custom_field_data'),
        ('virtualization', '0019_standardize_name_length'),
        ('virtualization', '0020_standardize_models'),
        ('virtualization', '0021_virtualmachine_vcpus_decimal'),
        ('virtualization', '0022_vminterface_parent'),

        # Squashed for v4.0
        ('virtualization', '0023_virtualmachine_natural_ordering'),
        ('virtualization', '0024_cluster_relax_uniqueness'),
        ('virtualization', '0025_extend_tag_support'),
        ('virtualization', '0026_vminterface_bridge'),
        ('virtualization', '0027_standardize_id_fields'),
        ('virtualization', '0028_vminterface_vrf'),
        ('virtualization', '0029_created_datetimefield'),
        ('virtualization', '0030_cluster_status'),
        ('virtualization', '0031_virtualmachine_site_device'),
        ('virtualization', '0032_virtualmachine_update_sites'),
        ('virtualization', '0033_unique_constraints'),
        ('virtualization', '0034_standardize_description_comments'),
        ('virtualization', '0035_virtualmachine_interface_count'),
        ('virtualization', '0036_virtualmachine_config_template'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('status', models.CharField(default='active', max_length=50)),
            ],
            options={
                'verbose_name': 'cluster',
                'verbose_name_plural': 'clusters',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VirtualMachine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('local_context_data', models.JSONField(blank=True, null=True)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('status', models.CharField(default='active', max_length=50)),
                ('vcpus', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('memory', models.PositiveIntegerField(blank=True, null=True)),
                ('disk', models.PositiveIntegerField(blank=True, null=True)),
                ('interface_count', utilities.fields.CounterCacheField(default=0, editable=False, to_field='virtual_machine', to_model='virtualization.VMInterface')),
                ('cluster', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='virtualization.cluster')),
                ('config_template', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='%(class)ss', to='extras.configtemplate')),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.device')),
                ('platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='virtual_machines', to='dcim.platform')),
                ('primary_ip4', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('primary_ip6', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('role', models.ForeignKey(blank=True, limit_choices_to={'vm_role': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.devicerole')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.site')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'virtual machine',
                'verbose_name_plural': 'virtual machines',
                'ordering': ('_name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='VMInterface',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('enabled', models.BooleanField(default=True)),
                ('mac_address', dcim.fields.MACAddressField(blank=True, null=True)),
                ('mtu', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65536)])),
                ('mode', models.CharField(blank=True, max_length=50)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize_interface)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('bridge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bridge_interfaces', to='virtualization.vminterface')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_interfaces', to='virtualization.vminterface')),
                ('tagged_vlans', models.ManyToManyField(blank=True, related_name='vminterfaces_as_tagged', to='ipam.vlan')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('untagged_vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vminterfaces_as_untagged', to='ipam.vlan')),
                ('virtual_machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='virtualization.virtualmachine')),
                ('vrf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vminterfaces', to='ipam.vrf')),
            ],
            options={
                'verbose_name': 'interface',
                'verbose_name_plural': 'interfaces',
                'ordering': ('virtual_machine', utilities.query_functions.CollateAsChar('_name')),
            },
            bases=(models.Model, utilities.tracking.TrackingModelMixin),
        ),
        migrations.CreateModel(
            name='ClusterType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'cluster type',
                'verbose_name_plural': 'cluster types',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ClusterGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'cluster group',
                'verbose_name_plural': 'cluster groups',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='cluster',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='virtualization.clustergroup'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='cluster',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='virtualization.clustertype'),
        ),
        migrations.AddConstraint(
            model_name='vminterface',
            constraint=models.UniqueConstraint(fields=('virtual_machine', 'name'), name='virtualization_vminterface_unique_virtual_machine_name'),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('cluster'), models.F('tenant'), name='virtualization_virtualmachine_unique_name_cluster_tenant'),
        ),
        migrations.AddConstraint(
            model_name='virtualmachine',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), models.F('cluster'), condition=models.Q(('tenant__isnull', True)), name='virtualization_virtualmachine_unique_name_cluster', violation_error_message='Virtual machine name must be unique per cluster.'),
        ),
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='virtualization_cluster_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='cluster',
            constraint=models.UniqueConstraint(fields=('site', 'name'), name='virtualization_cluster_unique_site_name'),
        ),
    ]
