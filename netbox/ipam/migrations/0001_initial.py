import django.contrib.postgres.fields
import django.core.serializers.json
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import ipam.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0002_auto_20160622_1821'),
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aggregate',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('date_added', models.DateField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ('prefix', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='IPAddress',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('address', ipam.fields.IPAddressField()),
                ('status', models.CharField(default='active', max_length=50)),
                ('role', models.CharField(blank=True, max_length=50)),
                ('assigned_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('dns_name', models.CharField(blank=True, max_length=255, validators=[django.core.validators.RegexValidator(code='invalid', message='Only alphanumeric characters, hyphens, periods, and underscores are allowed in DNS names', regex='^[0-9A-Za-z._-]+$')])),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'IP address',
                'verbose_name_plural': 'IP addresses',
                'ordering': ('address', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('prefix', ipam.fields.IPNetworkField()),
                ('status', models.CharField(default='active', max_length=50)),
                ('is_pool', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name_plural': 'prefixes',
                'ordering': (django.db.models.expressions.OrderBy(django.db.models.expressions.F('vrf'), nulls_first=True), 'prefix', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='RIR',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('is_private', models.BooleanField(default=False)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'RIR',
                'verbose_name_plural': 'RIRs',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RouteTarget',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=21, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='VRF',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('rd', models.CharField(blank=True, max_length=21, null=True, unique=True)),
                ('enforce_unique', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('export_targets', models.ManyToManyField(blank=True, related_name='exporting_vrfs', to='ipam.RouteTarget')),
                ('import_targets', models.ManyToManyField(blank=True, related_name='importing_vrfs', to='ipam.RouteTarget')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vrfs', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'VRF',
                'verbose_name_plural': 'VRFs',
                'ordering': ('name', 'rd', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='VLANGroup',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('scope_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('scope_type', models.ForeignKey(blank=True, limit_choices_to=models.Q(('model__in', ('region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster'))), null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'VLAN group',
                'verbose_name_plural': 'VLAN groups',
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='VLAN',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('vid', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4094)])),
                ('name', models.CharField(max_length=64)),
                ('status', models.CharField(default='active', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='ipam.vlangroup')),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vlans', to='ipam.role')),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='dcim.site')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='vlans', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'VLAN',
                'verbose_name_plural': 'VLANs',
                'ordering': ('site', 'group', 'vid', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('protocol', models.CharField(max_length=50)),
                ('ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)]), size=None)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='dcim.device')),
                ('ipaddresses', models.ManyToManyField(blank=True, related_name='services', to='ipam.IPAddress')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('protocol', 'ports', 'pk'),
            },
        ),
    ]
