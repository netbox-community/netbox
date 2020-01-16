import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.conf import settings
from django.db import connection, migrations, models
from django.db.utils import OperationalError

import extras.models


def verify_postgresql_version(apps, schema_editor):
    """
    Verify that PostgreSQL is version 9.4 or higher.
    """
    # https://www.postgresql.org/docs/current/libpq-status.html#LIBPQ-PQSERVERVERSION
    DB_MINIMUM_VERSION = 90400  # 9.4.0

    try:
        pg_version = connection.pg_version

        if pg_version < DB_MINIMUM_VERSION:
            raise Exception("PostgreSQL 9.4.0 ({}) or higher is required ({} found). Upgrade PostgreSQL and then run migrations again.".format(DB_MINIMUM_VERSION, pg_version))

    # Skip if the database is missing (e.g. for CI testing) or misconfigured.
    except OperationalError:
        pass


def is_filterable_to_filter_logic(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    CustomField.objects.filter(is_filterable=False).update(filter_logic=0)
    CustomField.objects.filter(is_filterable=True).update(filter_logic=1)
    # Select fields match on primary key only
    CustomField.objects.filter(is_filterable=True, type=600).update(filter_logic=2)


class Migration(migrations.Migration):

    replaces = [('extras', '0001_initial'), ('extras', '0002_custom_fields'), ('extras', '0003_exporttemplate_add_description'), ('extras', '0004_topologymap_change_comma_to_semicolon'), ('extras', '0005_useraction_add_bulk_create'), ('extras', '0006_add_imageattachments'), ('extras', '0007_unicode_literals'), ('extras', '0008_reports'), ('extras', '0009_topologymap_type'), ('extras', '0010_customfield_filter_logic'), ('extras', '0011_django2'), ('extras', '0012_webhooks'), ('extras', '0013_objectchange')]

    dependencies = [
        ('dcim', '0002_auto_20160622_1821'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(100, 'Text'), (200, 'Integer'), (300, 'Boolean (true/false)'), (400, 'Date'), (500, 'URL'), (600, 'Selection')], default=100)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('label', models.CharField(blank=True, help_text="Name of the field as displayed to users (if not provided, the field's name will be used)", max_length=50)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('required', models.BooleanField(default=False, help_text='Determines whether this field is required when creating new objects or editing an existing object.')),
                ('is_filterable', models.BooleanField(default=True, help_text='This field can be used to filter objects.')),
                ('default', models.CharField(blank=True, help_text='Default value for the field. Use "true" or "false" for booleans.', max_length=100)),
                ('weight', models.PositiveSmallIntegerField(default=100, help_text='Fields with higher weights appear lower in a form')),
                ('obj_type', models.ManyToManyField(help_text='The object(s) to which this field applies.', related_name='custom_fields', to='contenttypes.ContentType', verbose_name='Object(s)')),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('obj_id', models.PositiveIntegerField()),
                ('serialized_value', models.CharField(max_length=255)),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='extras.CustomField')),
                ('obj_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['obj_type', 'obj_id'],
                'unique_together': {('field', 'obj_type', 'obj_id')},
            },
        ),
        migrations.CreateModel(
            name='ExportTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('template_code', models.TextField()),
                ('mime_type', models.CharField(blank=True, max_length=15)),
                ('file_extension', models.CharField(blank=True, max_length=15)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'ordering': ['content_type', 'name'],
                'unique_together': {('content_type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='CustomFieldChoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('weight', models.PositiveSmallIntegerField(default=100, help_text='Higher weights appear lower in the list')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='extras.CustomField')),
            ],
            options={
                'ordering': ['field', 'weight', 'value'],
                'unique_together': {('field', 'value')},
            },
        ),
        migrations.CreateModel(
            name='Graph',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.PositiveSmallIntegerField(choices=[(100, 'Interface'), (200, 'Provider'), (300, 'Site')])),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('source', models.CharField(max_length=500, verbose_name='Source URL')),
                ('link', models.URLField(blank=True, verbose_name='Link URL')),
            ],
            options={
                'ordering': ['type', 'weight', 'name'],
            },
        ),
        migrations.CreateModel(
            name='ImageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('image', models.ImageField(height_field='image_height', upload_to=extras.models.image_upload, width_field='image_width')),
                ('image_height', models.PositiveSmallIntegerField()),
                ('image_width', models.PositiveSmallIntegerField()),
                ('name', models.CharField(blank=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TopologyMap',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('device_patterns', models.TextField(help_text='Identify devices to include in the diagram using regular expressions, one per line. Each line will result in a new tier of the drawing. Separate multiple regexes within a line using semicolons. Devices will be rendered in the order they are defined.')),
                ('description', models.CharField(blank=True, max_length=100)),
                ('site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='topology_maps', to='dcim.Site')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'created'), (7, 'bulk created'), (2, 'imported'), (3, 'modified'), (4, 'bulk edited'), (5, 'deleted'), (6, 'bulk deleted')])),
                ('message', models.TextField(blank=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
        migrations.RunPython(
            code=verify_postgresql_version,
        ),
        migrations.CreateModel(
            name='ReportResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('report', models.CharField(max_length=255, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('failed', models.BooleanField()),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['report'],
            },
        ),
        migrations.AddField(
            model_name='topologymap',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Network'), (2, 'Console'), (3, 'Power')], default=1),
        ),
        migrations.AddField(
            model_name='customfield',
            name='filter_logic',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Disabled'), (1, 'Loose'), (2, 'Exact')], default=1, help_text='Loose matches any instance of a given string; exact matches the entire field.'),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='required',
            field=models.BooleanField(default=False, help_text='If true, this field is required when creating new objects or editing an existing object.'),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='weight',
            field=models.PositiveSmallIntegerField(default=100, help_text='Fields with higher weights appear lower in a form.'),
        ),
        migrations.RunPython(
            code=is_filterable_to_filter_logic,
        ),
        migrations.RemoveField(
            model_name='customfield',
            name='is_filterable',
        ),
        migrations.AlterField(
            model_name='customfield',
            name='obj_type',
            field=models.ManyToManyField(help_text='The object(s) to which this field applies.', limit_choices_to={'model__in': ('provider', 'circuit', 'site', 'rack', 'devicetype', 'device', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'tenant', 'cluster', 'virtualmachine')}, related_name='custom_fields', to='contenttypes.ContentType', verbose_name='Object(s)'),
        ),
        migrations.AlterField(
            model_name='customfieldchoice',
            name='field',
            field=models.ForeignKey(limit_choices_to={'type': 600}, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='extras.CustomField'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ['provider', 'circuit', 'site', 'region', 'rack', 'rackgroup', 'manufacturer', 'devicetype', 'device', 'consoleport', 'powerport', 'interfaceconnection', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'tenant', 'cluster', 'virtualmachine']}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.CreateModel(
            name='Webhook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True)),
                ('type_create', models.BooleanField(default=False, help_text='Call this webhook when a matching object is created.')),
                ('type_update', models.BooleanField(default=False, help_text='Call this webhook when a matching object is updated.')),
                ('type_delete', models.BooleanField(default=False, help_text='Call this webhook when a matching object is deleted.')),
                ('payload_url', models.CharField(help_text='A POST will be sent to this URL when the webhook is called.', max_length=500, verbose_name='URL')),
                ('http_content_type', models.PositiveSmallIntegerField(choices=[(1, 'application/json'), (2, 'application/x-www-form-urlencoded')], default=1, verbose_name='HTTP content type')),
                ('secret', models.CharField(blank=True, help_text="When provided, the request will include a 'X-Hook-Signature' header containing a HMAC hex digest of the payload body using the secret as the key. The secret is not transmitted in the request.", max_length=255)),
                ('enabled', models.BooleanField(default=True)),
                ('ssl_verification', models.BooleanField(default=True, help_text='Enable SSL certificate verification. Disable with caution!', verbose_name='SSL verification')),
                ('obj_type', models.ManyToManyField(help_text='The object(s) to which this Webhook applies.', related_name='webhooks', to='contenttypes.ContentType', verbose_name='Object types')),
            ],
            options={
                'unique_together': {('payload_url', 'type_create', 'type_update', 'type_delete')},
            },
        ),
        migrations.CreateModel(
            name='ObjectChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('user_name', models.CharField(editable=False, max_length=150)),
                ('request_id', models.UUIDField(editable=False)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Created'), (2, 'Updated'), (3, 'Deleted')])),
                ('changed_object_id', models.PositiveIntegerField()),
                ('related_object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('object_repr', models.CharField(editable=False, max_length=200)),
                ('object_data', django.contrib.postgres.fields.jsonb.JSONField(editable=False)),
                ('changed_object_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
                ('related_object_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='changes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-time'],
            },
        ),
    ]
