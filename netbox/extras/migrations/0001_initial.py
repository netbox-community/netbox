from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import extras.fields
import extras.models.customfields
import extras.models.mixins
import extras.utils
import re
import taggit.managers
import utilities.fields
import utilities.json
import utilities.validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveBigIntegerField()),
            ],
            options={
                'verbose_name': 'bookmark',
                'verbose_name_plural': 'bookmarks',
                'ordering': ('created', 'pk'),
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
            ],
            options={
                'verbose_name': 'branch',
                'verbose_name_plural': 'branches',
                'ordering': ('name',),
            },
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
            ],
            options={
                'verbose_name': 'cached value',
                'verbose_name_plural': 'cached values',
                'ordering': ('weight', 'object_type', 'object_id'),
            },
        ),
        migrations.CreateModel(
            name='ConfigContext',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('auto_sync_enabled', models.BooleanField(default=False)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('data', models.JSONField()),
            ],
            options={
                'verbose_name': 'config context',
                'verbose_name_plural': 'config contexts',
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ConfigRevision',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(blank=True, max_length=200)),
                ('data', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'config revision',
                'verbose_name_plural': 'config revisions',
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='CustomFieldChoiceSet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('base_choices', models.CharField(blank=True, max_length=50)),
                ('extra_choices', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=2), blank=True, null=True, size=None)),
                ('order_alphabetically', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'custom field choice set',
                'verbose_name_plural': 'custom field choice sets',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(allow_unicode=True, max_length=100, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('color', utilities.fields.ColorField(default='9e9e9e', max_length=6)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('object_types', models.ManyToManyField(blank=True, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TaggedItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.IntegerField(db_index=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_tagged_items', to='contenttypes.contenttype')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_items', to='extras.tag')),
            ],
            options={
                'verbose_name': 'tagged item',
                'verbose_name_plural': 'tagged items',
            },
        ),
        migrations.CreateModel(
            name='ReportModule',
            fields=[
            ],
            options={
                'verbose_name': 'report module',
                'verbose_name_plural': 'report modules',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(extras.models.mixins.PythonModuleMixin, 'core.managedfile', models.Model),
        ),
        migrations.CreateModel(
            name='ScriptModule',
            fields=[
            ],
            options={
                'verbose_name': 'script module',
                'verbose_name_plural': 'script modules',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(extras.models.mixins.PythonModuleMixin, 'core.managedfile', models.Model),
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('type_create', models.BooleanField(default=False)),
                ('type_update', models.BooleanField(default=False)),
                ('type_delete', models.BooleanField(default=False)),
                ('type_job_start', models.BooleanField(default=False)),
                ('type_job_end', models.BooleanField(default=False)),
                ('payload_url', models.CharField(max_length=500)),
                ('enabled', models.BooleanField(default=True)),
                ('http_method', models.CharField(default='POST', max_length=30)),
                ('http_content_type', models.CharField(default='application/json', max_length=100)),
                ('additional_headers', models.TextField(blank=True)),
                ('body_template', models.TextField(blank=True)),
                ('secret', models.CharField(blank=True, max_length=255)),
                ('conditions', models.JSONField(blank=True, null=True)),
                ('ssl_verification', models.BooleanField(default=True)),
                ('ca_file_path', models.CharField(blank=True, max_length=4096, null=True)),
                ('content_types', models.ManyToManyField(related_name='webhooks', to='contenttypes.contenttype')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'webhook',
                'verbose_name_plural': 'webhooks',
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
                ('branch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='staged_changes', to='extras.branch')),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'staged change',
                'verbose_name_plural': 'staged changes',
                'ordering': ('pk',),
            },
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
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'saved filter',
                'verbose_name_plural': 'saved filters',
                'ordering': ('weight', 'name'),
            },
        ),
        migrations.CreateModel(
            name='ObjectChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user_name', models.CharField(editable=False, max_length=150)),
                ('request_id', models.UUIDField(db_index=True, editable=False)),
                ('action', models.CharField(max_length=50)),
                ('changed_object_id', models.PositiveBigIntegerField()),
                ('related_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('object_repr', models.CharField(editable=False, max_length=200)),
                ('prechange_data', models.JSONField(blank=True, editable=False, null=True)),
                ('postchange_data', models.JSONField(blank=True, editable=False, null=True)),
                ('changed_object_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('related_object_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'object change',
                'verbose_name_plural': 'object changes',
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('assigned_object_id', models.PositiveBigIntegerField()),
                ('kind', models.CharField(default='info', max_length=30)),
                ('comments', models.TextField()),
                ('assigned_object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'journal entry',
                'verbose_name_plural': 'journal entries',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('image', models.ImageField(height_field='image_height', upload_to=extras.utils.image_upload, width_field='image_width')),
                ('image_height', models.PositiveSmallIntegerField()),
                ('image_width', models.PositiveSmallIntegerField()),
                ('name', models.CharField(blank=True, max_length=50)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'image attachment',
                'verbose_name_plural': 'image attachments',
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='ExportTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('auto_sync_enabled', models.BooleanField(default=False)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('template_code', models.TextField()),
                ('mime_type', models.CharField(blank=True, max_length=50)),
                ('file_extension', models.CharField(blank=True, max_length=15)),
                ('as_attachment', models.BooleanField(default=True)),
                ('content_types', models.ManyToManyField(related_name='export_templates', to='contenttypes.contenttype')),
                ('data_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile')),
                ('data_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource')),
            ],
            options={
                'verbose_name': 'export template',
                'verbose_name_plural': 'export templates',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('layout', models.JSONField(default=list)),
                ('config', models.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'dashboard',
                'verbose_name_plural': 'dashboards',
            },
        ),
        migrations.CreateModel(
            name='CustomLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('link_text', models.TextField()),
                ('link_url', models.TextField()),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('group_name', models.CharField(blank=True, max_length=50)),
                ('button_class', models.CharField(default='outline-dark', max_length=30)),
                ('new_window', models.BooleanField(default=False)),
                ('content_types', models.ManyToManyField(related_name='custom_links', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'custom link',
                'verbose_name_plural': 'custom links',
                'ordering': ['group_name', 'weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('type', models.CharField(default='text', max_length=50)),
                ('name', models.CharField(max_length=50, unique=True, validators=[django.core.validators.RegexValidator(flags=re.RegexFlag['IGNORECASE'], message='Only alphanumeric characters and underscores are allowed.', regex='^[a-z0-9_]+$'), django.core.validators.RegexValidator(flags=re.RegexFlag['IGNORECASE'], inverse_match=True, message='Double underscores are not permitted in custom field names.', regex='__')])),
                ('label', models.CharField(blank=True, max_length=50)),
                ('group_name', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('required', models.BooleanField(default=False)),
                ('search_weight', models.PositiveSmallIntegerField(default=1000)),
                ('filter_logic', models.CharField(default='loose', max_length=50)),
                ('default', models.JSONField(blank=True, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('validation_minimum', models.IntegerField(blank=True, null=True)),
                ('validation_maximum', models.IntegerField(blank=True, null=True)),
                ('validation_regex', models.CharField(blank=True, max_length=500, validators=[utilities.validators.validate_regex])),
                ('ui_visibility', models.CharField(default='read-write', max_length=50)),
                ('is_cloneable', models.BooleanField(default=False)),
                ('choice_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='choices_for', to='extras.customfieldchoiceset')),
                ('content_types', models.ManyToManyField(related_name='custom_fields', to='contenttypes.contenttype')),
                ('object_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'custom field',
                'verbose_name_plural': 'custom fields',
                'ordering': ['group_name', 'weight', 'name'],
            },
            managers=[
                ('objects', extras.models.customfields.CustomFieldManager()),
            ],
        ),
        migrations.CreateModel(
            name='ConfigTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('data_path', models.CharField(blank=True, editable=False, max_length=1000)),
                ('auto_sync_enabled', models.BooleanField(default=False)),
                ('data_synced', models.DateTimeField(blank=True, editable=False, null=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('template_code', models.TextField()),
                ('environment_params', models.JSONField(blank=True, default=dict, null=True)),
                ('data_file', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile')),
                ('data_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'config template',
                'verbose_name_plural': 'config templates',
                'ordering': ('name',),
            },
        ),
    ]
