from django.db import migrations, models
import django.db.models.deletion
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Circuit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('cid', models.CharField(max_length=100)),
                ('status', models.CharField(default='active', max_length=50)),
                ('install_date', models.DateField(blank=True, null=True)),
                ('termination_date', models.DateField(blank=True, null=True)),
                ('commit_rate', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'circuit',
                'verbose_name_plural': 'circuits',
                'ordering': ['provider', 'provider_account', 'cid'],
            },
        ),
        migrations.CreateModel(
            name='CircuitTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('cable_end', models.CharField(blank=True, max_length=1)),
                ('mark_connected', models.BooleanField(default=False)),
                ('term_side', models.CharField(max_length=1)),
                ('port_speed', models.PositiveIntegerField(blank=True, null=True)),
                ('upstream_speed', models.PositiveIntegerField(blank=True, null=True)),
                ('xconnect_id', models.CharField(blank=True, max_length=50)),
                ('pp_info', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'circuit termination',
                'verbose_name_plural': 'circuit terminations',
                'ordering': ['circuit', 'term_side'],
            },
        ),
        migrations.CreateModel(
            name='CircuitType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'circuit type',
                'verbose_name_plural': 'circuit types',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'provider',
                'verbose_name_plural': 'providers',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProviderAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('account', models.CharField(max_length=100)),
                ('name', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'verbose_name': 'provider account',
                'verbose_name_plural': 'provider accounts',
                'ordering': ('provider', 'account'),
            },
        ),
        migrations.CreateModel(
            name='ProviderNetwork',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('service_id', models.CharField(blank=True, max_length=100)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='networks', to='circuits.provider')),
            ],
            options={
                'verbose_name': 'provider network',
                'verbose_name_plural': 'provider networks',
                'ordering': ('provider', 'name'),
            },
        ),
    ]
