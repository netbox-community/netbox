import re
import uuid

import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models

import extras.fields
import utilities.json


class Migration(migrations.Migration):
    replaces = [
        ('extras', '0060_customlink_button_class'),
        ('extras', '0061_extras_change_logging'),
        ('extras', '0062_clear_secrets_changelog'),
        ('extras', '0063_webhook_conditions'),
        ('extras', '0064_configrevision'),
        ('extras', '0065_imageattachment_change_logging'),
        ('extras', '0066_customfield_name_validation'),
        ('extras', '0067_customfield_min_max_values'),
        ('extras', '0068_configcontext_cluster_types'),
        ('extras', '0069_custom_object_field'),
        ('extras', '0070_customlink_enabled'),
        ('extras', '0071_standardize_id_fields'),
        ('extras', '0072_created_datetimefield'),
        ('extras', '0073_journalentry_tags_custom_fields'),
        ('extras', '0074_customfield_extensions'),
        ('extras', '0075_configcontext_locations'),
        ('extras', '0076_tag_slug_unicode'),
        ('extras', '0077_customlink_extend_text_and_url'),
        ('extras', '0078_unique_constraints'),
        ('extras', '0079_scheduled_jobs'),
        ('extras', '0080_customlink_content_types'),
        ('extras', '0081_exporttemplate_content_types'),
        ('extras', '0082_savedfilter'),
        ('extras', '0083_search'),
        ('extras', '0084_staging'),
        ('extras', '0085_synced_data'),
        ('extras', '0086_configtemplate'),
    ]

    dependencies = [
        ('virtualization', '0001_squashed_0022'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('wireless', '0008_wirelesslan_status'),
        ('dcim', '0166_virtualdevicecontext'),
        ('tenancy', '0009_standardize_description_comments'),
        ('extras', '0059_exporttemplate_as_attachment'),
        ('circuits', '0041_standardize_description_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlink',
            name='button_class',
            field=models.CharField(default='outline-dark', max_length=30),
        ),
        migrations.AddField(
            model_name='customfield',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customfield',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='customlink',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customlink',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='webhook',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='webhook',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='webhook',
            name='conditions',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='imageattachment',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='name',
            field=models.CharField(
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        message='Only alphanumeric characters and underscores are allowed.',
                        regex='^[a-z0-9_]+$',
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        inverse_match=True,
                        message='Double underscores are not permitted in custom field names.',
                        regex='__',
                    ),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='validation_maximum',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='validation_minimum',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='cluster_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='virtualization.clustertype'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='object_type',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype'
            ),
        ),
        migrations.AddField(
            model_name='customlink',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='configcontext',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.CreateModel(
            name='ConfigRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(blank=True, max_length=200)),
                ('data', models.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='customfield',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='imageattachment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='jobresult',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='taggeditem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='imageattachment',
            name='object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='assigned_object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='changed_object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='related_object_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='configcontext',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='imageattachment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='tag',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AddField(
            model_name='journalentry',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AlterModelOptions(
            name='customfield',
            options={'ordering': ['group_name', 'weight', 'name']},
        ),
        migrations.AddField(
            model_name='customfield',
            name='group_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='customfield',
            name='ui_visibility',
            field=models.CharField(default='read-write', max_length=50),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='locations',
            field=models.ManyToManyField(blank=True, related_name='+', to='dcim.location'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(allow_unicode=True, max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='link_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='link_url',
            field=models.TextField(),
        ),
        migrations.AlterUniqueTogether(
            name='exporttemplate',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='webhook',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='exporttemplate',
            constraint=models.UniqueConstraint(
                fields=('content_type', 'name'), name='extras_exporttemplate_unique_content_type_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='webhook',
            constraint=models.UniqueConstraint(
                fields=('payload_url', 'type_create', 'type_update', 'type_delete'),
                name='extras_webhook_unique_payload_url_types',
            ),
        ),
        migrations.AddField(
            model_name='jobresult',
            name='scheduled',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='jobresult',
            name='interval',
            field=models.PositiveIntegerField(
                blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]
            ),
        ),
        migrations.AddField(
            model_name='jobresult',
            name='started',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='jobresult',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='customlink',
            name='content_types',
            field=models.ManyToManyField(related_name='custom_links', to='contenttypes.contenttype'),
        ),
        migrations.RemoveField(
            model_name='customlink',
            name='content_type',
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='content_types',
            field=models.ManyToManyField(related_name='export_templates', to='contenttypes.contenttype'),
        ),
        migrations.RemoveConstraint(
            model_name='exporttemplate',
            name='extras_exporttemplate_unique_content_type_name',
        ),
        migrations.RemoveField(
            model_name='exporttemplate',
            name='content_type',
        ),
        migrations.AlterModelOptions(
            name='exporttemplate',
            options={'ordering': ('name',)},
        ),
        migrations.CreateModel(
            name='SavedFilter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('enabled', models.BooleanField(default=True)),
                ('shared', models.BooleanField(default=True)),
                ('parameters', models.JSONField()),
                ('content_types', models.ManyToManyField(related_name='saved_filters', to='contenttypes.contenttype')),
                (
                    'user',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                'ordering': ('weight', 'name'),
            },
        ),
        migrations.AddField(
            model_name='customfield',
            name='search_weight',
            field=models.PositiveSmallIntegerField(default=1000),
        ),
        migrations.CreateModel(
            name='CachedValue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('field', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=30)),
                ('value', extras.fields.CachedValueField()),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                (
                    'object_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype'
                    ),
                ),
            ],
            options={
                'ordering': ('weight', 'object_type', 'object_id'),
            },
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'user',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='StagedChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('action', models.CharField(max_length=20)),
                ('object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('data', models.JSONField(blank=True, null=True)),
                (
                    'branch',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='staged_changes', to='extras.branch'
                    ),
                ),
                (
                    'object_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype'
                    ),
                ),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_file',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='core.datafile',
            ),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_path',
            field=models.CharField(blank=True, editable=False, max_length=1000),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_source',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='core.datasource',
            ),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='auto_sync_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_synced',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_file',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to='core.datafile',
            ),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_path',
            field=models.CharField(blank=True, editable=False, max_length=1000),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_source',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='core.datasource',
            ),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='auto_sync_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_synced',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        migrations.CreateModel(
            name='ConfigTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('template_code', models.TextField()),
                ('environment_params', models.JSONField(blank=True, default=dict, null=True)),
                (
                    'data_file',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='+',
                        to='core.datafile',
                    ),
                ),
                (
                    'data_source',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='core.datasource',
                    ),
                ),
                ('auto_sync_enabled', models.BooleanField(default=False)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
