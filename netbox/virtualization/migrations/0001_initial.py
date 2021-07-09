import dcim.fields
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.fields
import utilities.ordering
import utilities.query_functions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0002_initial'),
        ('ipam', '0001_initial'),
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cluster',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ClusterGroup',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ClusterType',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VirtualMachine',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('local_context_data', models.JSONField(blank=True, null=True)),
                ('name', models.CharField(max_length=64)),
                ('status', models.CharField(default='active', max_length=50)),
                ('vcpus', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True, validators=[django.core.validators.MinValueValidator(0.01)])),
                ('memory', models.PositiveIntegerField(blank=True, null=True)),
                ('disk', models.PositiveIntegerField(blank=True, null=True)),
                ('comments', models.TextField(blank=True)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='virtualization.cluster')),
                ('platform', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='virtual_machines', to='dcim.platform')),
                ('primary_ip4', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('primary_ip6', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress')),
                ('role', models.ForeignKey(blank=True, limit_choices_to={'vm_role': True}, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.devicerole')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='tenancy.tenant')),
            ],
            options={
                'ordering': ('name', 'pk'),
                'unique_together': {('cluster', 'tenant', 'name')},
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
        migrations.CreateModel(
            name='VMInterface',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(default=True)),
                ('mac_address', dcim.fields.MACAddressField(blank=True, null=True)),
                ('mtu', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65536)])),
                ('mode', models.CharField(blank=True, max_length=50)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize_interface)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_interfaces', to='virtualization.vminterface')),
                ('tagged_vlans', models.ManyToManyField(blank=True, related_name='vminterfaces_as_tagged', to='ipam.VLAN')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('untagged_vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vminterfaces_as_untagged', to='ipam.vlan')),
                ('virtual_machine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='interfaces', to='virtualization.virtualmachine')),
            ],
            options={
                'verbose_name': 'interface',
                'ordering': ('virtual_machine', utilities.query_functions.CollateAsChar('_name')),
                'unique_together': {('virtual_machine', 'name')},
            },
        ),
    ]
