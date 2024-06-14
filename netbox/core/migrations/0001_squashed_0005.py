import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('core', '0001_initial'),
        ('core', '0002_managedfile'),
        ('core', '0003_job'),
        ('core', '0004_replicate_jobresults'),
        ('core', '0005_job_created_auto_now')
    ]

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('extras', '0002_squashed_0059'),
    ]

    operations = [
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
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
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
                ('source', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='datafiles', to='core.datasource')),
            ],
            options={
                'ordering': ('source', 'path'),
            },
        ),
        migrations.AddConstraint(
            model_name='datafile',
            constraint=models.UniqueConstraint(fields=('source', 'path'), name='core_datafile_unique_source_path'),
        ),
        migrations.AddIndex(
            model_name='datafile',
            index=models.Index(fields=['source', 'path'], name='core_datafile_source_path'),
        ),
        migrations.CreateModel(
            name='AutoSyncRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveBigIntegerField()),
                ('datafile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.datafile')),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'indexes': [models.Index(fields=['object_type', 'object_id'], name='core_autosy_object__c17bac_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='autosyncrecord',
            constraint=models.UniqueConstraint(fields=('object_type', 'object_id'), name='core_autosyncrecord_object'),
        ),
        migrations.CreateModel(
            name='ManagedFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(blank=True, editable=False, null=True)),
                ('file_root', models.CharField(max_length=1000)),
                ('file_path', models.FilePathField(editable=False)),
                ('data_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile')),
                ('data_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource')),
                ('auto_sync_enabled', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('file_root', 'file_path'),
                'indexes': [models.Index(fields=['file_root', 'file_path'], name='core_managedfile_root_path')],
            },
        ),
        migrations.AddConstraint(
            model_name='managedfile',
            constraint=models.UniqueConstraint(fields=('file_root', 'file_path'), name='core_managedfile_unique_root_path'),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('name', models.CharField(max_length=200)),
                ('created', models.DateTimeField()),
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
                'ordering': ['-created'],
            },
        ),
        migrations.AlterField(
            model_name='job',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
