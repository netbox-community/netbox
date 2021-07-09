import dcim.fields
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    replaces = [
        ('circuits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Circuit',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('cid', models.CharField(max_length=100)),
                ('status', models.CharField(default='active', max_length=50)),
                ('install_date', models.DateField(blank=True, null=True)),
                ('commit_rate', models.PositiveIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['provider', 'cid'],
            },
        ),
        migrations.CreateModel(
            name='CircuitTermination',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('_cable_peer_id', models.PositiveIntegerField(blank=True, null=True)),
                ('mark_connected', models.BooleanField(default=False)),
                ('term_side', models.CharField(max_length=1)),
                ('port_speed', models.PositiveIntegerField(blank=True, null=True)),
                ('upstream_speed', models.PositiveIntegerField(blank=True, null=True)),
                ('xconnect_id', models.CharField(blank=True, max_length=50)),
                ('pp_info', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['circuit', 'term_side'],
            },
        ),
        migrations.CreateModel(
            name='CircuitType',
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
            name='Provider',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('asn', dcim.fields.ASNField(blank=True, null=True)),
                ('account', models.CharField(blank=True, max_length=30)),
                ('portal_url', models.URLField(blank=True)),
                ('noc_contact', models.TextField(blank=True)),
                ('admin_contact', models.TextField(blank=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProviderNetwork',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='networks', to='circuits.provider')),
            ],
            options={
                'ordering': ('provider', 'name'),
            },
        ),
    ]
