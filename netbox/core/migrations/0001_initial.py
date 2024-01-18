from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import extras.utils
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AutoSyncRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveBigIntegerField()),
            ],
            options={
                'verbose_name': 'auto sync record',
                'verbose_name_plural': 'auto sync records',
            },
        ),
        migrations.CreateModel(
            name='DataFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(editable=False)),
                ('path', models.CharField(editable=False, max_length=1000)),
                ('size', models.PositiveIntegerField(editable=False)),
                ('hash', models.CharField(editable=False, max_length=64, validators=[django.core.validators.RegexValidator(message='Length must be 64 hexadecimal characters.', regex='^[0-9a-f]{64}$')])),
                ('data', models.BinaryField()),
            ],
            options={
                'verbose_name': 'data file',
                'verbose_name_plural': 'data files',
                'ordering': ('source', 'path'),
            },
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('type', models.CharField(default='local', max_length=50)),
                ('source_url', models.CharField(max_length=200)),
                ('status', models.CharField(default='new', editable=False, max_length=50)),
                ('enabled', models.BooleanField(default=True)),
                ('ignore_rules', models.TextField(blank=True)),
                ('parameters', models.JSONField(blank=True, null=True)),
                ('last_synced', models.DateTimeField(blank=True, editable=False, null=True)),
            ],
            options={
                'verbose_name': 'data source',
                'verbose_name_plural': 'data sources',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ManagedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('auto_sync_enabled', models.BooleanField(default=False)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(blank=True, editable=False, null=True)),
                ('file_root', models.CharField(max_length=1000)),
                ('file_path', models.FilePathField(editable=False)),
                ('data_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile')),
                ('data_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource')),
            ],
            options={
                'verbose_name': 'managed file',
                'verbose_name_plural': 'managed files',
                'ordering': ('file_root', 'file_path'),
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('scheduled', models.DateTimeField(blank=True, null=True)),
                ('interval', models.PositiveIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('started', models.DateTimeField(blank=True, null=True)),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='pending', max_length=30)),
                ('data', models.JSONField(blank=True, null=True)),
                ('job_id', models.UUIDField(unique=True)),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'job',
                'verbose_name_plural': 'jobs',
                'ordering': ['-created'],
            },
        ),
    ]
