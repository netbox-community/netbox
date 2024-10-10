import django.contrib.postgres.fields
import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models

import extras.models.mixins
import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('extras', '0087_dashboard'),
        ('extras', '0088_jobresult_webhooks'),
        ('extras', '0089_customfield_is_cloneable'),
        ('extras', '0090_objectchange_index_request_id'),
        ('extras', '0091_create_managedfiles'),
        ('extras', '0092_delete_jobresult'),
        ('extras', '0093_configrevision_ordering'),
        ('extras', '0094_tag_object_types'),
        ('extras', '0095_bookmarks'),
        ('extras', '0096_customfieldchoiceset'),
        ('extras', '0097_customfield_remove_choices'),
        ('extras', '0098_webhook_custom_field_data_webhook_tags')
    ]

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0086_configtemplate'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0002_managedfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dashboard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('layout', models.JSONField(default=list)),
                ('config', models.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dashboard', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='webhook',
            name='type_job_end',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='webhook',
            name='type_job_start',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='customfield',
            name='is_cloneable',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='request_id',
            field=models.UUIDField(db_index=True, editable=False),
        ),
        migrations.CreateModel(
            name='ReportModule',
            fields=[
            ],
            options={
                'proxy': True,
                'ordering': ('file_root', 'file_path'),
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
                'proxy': True,
                'ordering': ('file_root', 'file_path'),
                'indexes': [],
                'constraints': [],
            },
            bases=(extras.models.mixins.PythonModuleMixin, 'core.managedfile', models.Model),
        ),
        migrations.DeleteModel(
            name='JobResult',
        ),
        migrations.AlterModelOptions(
            name='configrevision',
            options={'ordering': ['-created']},
        ),
        migrations.AddField(
            model_name='tag',
            name='object_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddIndex(
            model_name='taggeditem',
            index=models.Index(fields=['content_type', 'object_id'], name='extras_tagg_content_717743_idx'),
        ),
        migrations.CreateModel(
            name='Bookmark',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created', 'pk'),
            },
        ),
        migrations.AddConstraint(
            model_name='bookmark',
            constraint=models.UniqueConstraint(fields=('object_type', 'object_id', 'user'), name='extras_bookmark_unique_per_object_and_user'),
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
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='customfield',
            name='choice_set',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='choices_for', to='extras.customfieldchoiceset'),
        ),
        migrations.RemoveField(
            model_name='customfield',
            name='choices',
        ),
        migrations.AddField(
            model_name='webhook',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AddField(
            model_name='webhook',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
