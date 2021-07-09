from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import extras.models.customfields
import extras.utils
import utilities.fields
import utilities.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    replaces = [
        ('extras', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ConfigContext',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('data', models.JSONField()),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('color', utilities.fields.ColorField(default='9e9e9e', max_length=6)),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('type_create', models.BooleanField(default=False)),
                ('type_update', models.BooleanField(default=False)),
                ('type_delete', models.BooleanField(default=False)),
                ('payload_url', models.CharField(max_length=500)),
                ('enabled', models.BooleanField(default=True)),
                ('http_method', models.CharField(default='POST', max_length=30)),
                ('http_content_type', models.CharField(default='application/json', max_length=100)),
                ('additional_headers', models.TextField(blank=True)),
                ('body_template', models.TextField(blank=True)),
                ('secret', models.CharField(blank=True, max_length=255)),
                ('ssl_verification', models.BooleanField(default=True)),
                ('ca_file_path', models.CharField(blank=True, max_length=4096, null=True)),
                ('content_types', models.ManyToManyField(limit_choices_to=extras.utils.FeatureQuery('webhooks'), related_name='webhooks', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TaggedItem',
            fields=[
                ('object_id', models.IntegerField(db_index=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras_taggeditem_tagged_items', to='contenttypes.contenttype')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras_taggeditem_items', to='extras.tag')),
            ],
        ),
        migrations.CreateModel(
            name='ObjectChange',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('time', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('user_name', models.CharField(editable=False, max_length=150)),
                ('request_id', models.UUIDField(editable=False)),
                ('action', models.CharField(max_length=50)),
                ('changed_object_id', models.PositiveIntegerField()),
                ('related_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('object_repr', models.CharField(editable=False, max_length=200)),
                ('prechange_data', models.JSONField(blank=True, editable=False, null=True)),
                ('postchange_data', models.JSONField(blank=True, editable=False, null=True)),
                ('changed_object_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('related_object_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.CreateModel(
            name='JournalEntry',
            fields=[
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('assigned_object_id', models.PositiveIntegerField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('kind', models.CharField(default='info', max_length=30)),
                ('comments', models.TextField()),
                ('assigned_object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'journal entries',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='JobResult',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('completed', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(default='pending', max_length=30)),
                ('data', models.JSONField(blank=True, null=True)),
                ('job_id', models.UUIDField(unique=True)),
                ('obj_type', models.ForeignKey(limit_choices_to=extras.utils.FeatureQuery('job_results'), on_delete=django.db.models.deletion.CASCADE, related_name='job_results', to='contenttypes.contenttype')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['obj_type', 'name', '-created'],
            },
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('image', models.ImageField(height_field='image_height', upload_to=extras.utils.image_upload, width_field='image_width')),
                ('image_height', models.PositiveSmallIntegerField()),
                ('image_width', models.PositiveSmallIntegerField()),
                ('name', models.CharField(blank=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='ExportTemplate',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('template_code', models.TextField()),
                ('mime_type', models.CharField(blank=True, max_length=50)),
                ('file_extension', models.CharField(blank=True, max_length=15)),
                ('as_attachment', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(limit_choices_to=extras.utils.FeatureQuery('export_templates'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['content_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomLink',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('link_text', models.CharField(max_length=500)),
                ('link_url', models.CharField(max_length=500)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('group_name', models.CharField(blank=True, max_length=50)),
                ('button_class', models.CharField(default='default', max_length=30)),
                ('new_window', models.BooleanField(default=False)),
                ('content_type', models.ForeignKey(limit_choices_to=extras.utils.FeatureQuery('custom_links'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['group_name', 'weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(default='text', max_length=50)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('label', models.CharField(blank=True, max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('required', models.BooleanField(default=False)),
                ('filter_logic', models.CharField(default='loose', max_length=50)),
                ('default', models.JSONField(blank=True, null=True)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('validation_minimum', models.PositiveIntegerField(blank=True, null=True)),
                ('validation_maximum', models.PositiveIntegerField(blank=True, null=True)),
                ('validation_regex', models.CharField(blank=True, max_length=500, validators=[utilities.validators.validate_regex])),
                ('choices', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), blank=True, null=True, size=None)),
                ('content_types', models.ManyToManyField(limit_choices_to=extras.utils.FeatureQuery('custom_fields'), related_name='custom_fields', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
            managers=[
                ('objects', extras.models.customfields.CustomFieldManager()),
            ],
        ),
    ]
