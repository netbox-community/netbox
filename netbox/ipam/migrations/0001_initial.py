import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import ipam.fields
import ipam.models.ip
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('date_added', models.DateField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'aggregate',
                'verbose_name_plural': 'aggregates',
                'ordering': ('prefix', 'pk'),
            },
            bases=(ipam.models.ip.GetAvailablePrefixesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ASN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('asn', ipam.fields.ASNField(unique=True)),
            ],
            options={
                'verbose_name': 'ASN',
                'verbose_name_plural': 'ASNs',
                'ordering': ['asn'],
            },
        ),
        migrations.CreateModel(
            name='ASNRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('start', ipam.fields.ASNField()),
                ('end', ipam.fields.ASNField()),
            ],
            options={
                'verbose_name': 'ASN range',
                'verbose_name_plural': 'ASN ranges',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='FHRPGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('group_id', models.PositiveSmallIntegerField()),
                ('name', models.CharField(blank=True, max_length=100)),
                ('protocol', models.CharField(max_length=50)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('auth_key', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'verbose_name': 'FHRP group',
                'verbose_name_plural': 'FHRP groups',
                'ordering': ['protocol', 'group_id', 'pk'],
            },
        ),
        migrations.CreateModel(
            name='FHRPGroupAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('interface_id', models.PositiveBigIntegerField()),
                ('priority', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)])),
            ],
            options={
                'verbose_name': 'FHRP group assignment',
                'verbose_name_plural': 'FHRP group assignments',
                'ordering': ('-priority', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('address', ipam.fields.IPAddressField()),
                ('status', models.CharField(default='active', max_length=50)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('assigned_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('dns_name', models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator(code='invalid', message='Only alphanumeric characters, asterisks, hyphens, periods, and underscores are allowed in DNS names', regex='^([0-9A-Za-z_-]+|\\*)(\\.[0-9A-Za-z_-]+)*\\.?$')])),
            ],
            options={
                'verbose_name': 'IP address',
                'verbose_name_plural': 'IP addresses',
                'ordering': ('address', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='IPRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('start_address', ipam.fields.IPAddressField()),
                ('end_address', ipam.fields.IPAddressField()),
                ('size', models.PositiveIntegerField(editable=False)),
                ('status', models.CharField(default='active', max_length=50)),
                ('mark_utilized', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'IP range',
                'verbose_name_plural': 'IP ranges',
                'ordering': (models.OrderBy(models.F('vrf'), nulls_first=True), 'start_address', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='L2VPN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('type', models.CharField(max_length=50)),
                ('identifier', models.BigIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'L2VPN',
                'verbose_name_plural': 'L2VPNs',
                'ordering': ('name', 'identifier'),
            },
        ),
        migrations.CreateModel(
            name='L2VPNTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('assigned_object_id', models.PositiveBigIntegerField()),
            ],
            options={
                'verbose_name': 'L2VPN termination',
                'verbose_name_plural': 'L2VPN terminations',
                'ordering': ('l2vpn',),
            },
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('status', models.CharField(default='active', max_length=50)),
                ('is_pool', models.BooleanField(default=False)),
                ('mark_utilized', models.BooleanField(default=False)),
                ('_depth', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('_children', models.PositiveBigIntegerField(default=0, editable=False)),
            ],
            options={
                'verbose_name': 'prefix',
                'verbose_name_plural': 'prefixes',
                'ordering': (models.OrderBy(models.F('vrf'), nulls_first=True), 'prefix', 'pk'),
            },
            bases=(ipam.models.ip.GetAvailablePrefixesMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RIR',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_private', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'RIR',
                'verbose_name_plural': 'RIRs',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
            ],
            options={
                'verbose_name': 'role',
                'verbose_name_plural': 'roles',
                'ordering': ('weight', 'name'),
            },
        ),
        migrations.CreateModel(
            name='RouteTarget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=21, unique=True)),
            ],
            options={
                'verbose_name': 'route target',
                'verbose_name_plural': 'route targets',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('protocol', models.CharField(max_length=50)),
                ('ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)]), size=None)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name': 'service',
                'verbose_name_plural': 'services',
                'ordering': ('protocol', 'ports', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='ServiceTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('protocol', models.CharField(max_length=50)),
                ('ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)]), size=None)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'service template',
                'verbose_name_plural': 'service templates',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='VLAN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('vid', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4094)])),
                ('name', models.CharField(max_length=64)),
                ('status', models.CharField(default='active', max_length=50)),
            ],
            options={
                'verbose_name': 'VLAN',
                'verbose_name_plural': 'VLANs',
                'ordering': ('site', 'group', 'vid', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='VLANGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('scope_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('min_vid', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4094)])),
                ('max_vid', models.PositiveSmallIntegerField(default=4094, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4094)])),
            ],
            options={
                'verbose_name': 'VLAN group',
                'verbose_name_plural': 'VLAN groups',
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='VRF',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('rd', models.CharField(blank=True, max_length=21, null=True, unique=True)),
                ('enforce_unique', models.BooleanField(default=True)),
                ('export_targets', models.ManyToManyField(blank=True, related_name='exporting_vrfs', to='ipam.routetarget')),
                ('import_targets', models.ManyToManyField(blank=True, related_name='importing_vrfs', to='ipam.routetarget')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'VRF',
                'verbose_name_plural': 'VRFs',
                'ordering': ('name', 'rd', 'pk'),
            },
        ),
    ]
