import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models

import extras.models

CUSTOMFIELD_TYPE_CHOICES = (
    (100, 'text'),
    (200, 'integer'),
    (300, 'boolean'),
    (400, 'date'),
    (500, 'url'),
    (600, 'select')
)

CUSTOMFIELD_FILTER_LOGIC_CHOICES = (
    (0, 'disabled'),
    (1, 'integer'),
    (2, 'exact'),
)

OBJECTCHANGE_ACTION_CHOICES = (
    (1, 'create'),
    (2, 'update'),
    (3, 'delete'),
)

EXPORTTEMPLATE_LANGUAGE_CHOICES = (
    (10, 'django'),
    (20, 'jinja2'),
)

WEBHOOK_CONTENTTYPE_CHOICES = (
    (1, 'application/json'),
    (2, 'application/x-www-form-urlencoded'),
)

GRAPH_TYPE_CHOICES = (
    (100, 'dcim', 'interface'),
    (150, 'dcim', 'device'),
    (200, 'circuits', 'provider'),
    (300, 'dcim', 'site'),
)


def customfield_type_to_slug(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    for id, slug in CUSTOMFIELD_TYPE_CHOICES:
        CustomField.objects.filter(type=str(id)).update(type=slug)


def customfield_filter_logic_to_slug(apps, schema_editor):
    CustomField = apps.get_model('extras', 'CustomField')
    for id, slug in CUSTOMFIELD_FILTER_LOGIC_CHOICES:
        CustomField.objects.filter(filter_logic=str(id)).update(filter_logic=slug)


def objectchange_action_to_slug(apps, schema_editor):
    ObjectChange = apps.get_model('extras', 'ObjectChange')
    for id, slug in OBJECTCHANGE_ACTION_CHOICES:
        ObjectChange.objects.filter(action=str(id)).update(action=slug)


def exporttemplate_language_to_slug(apps, schema_editor):
    ExportTemplate = apps.get_model('extras', 'ExportTemplate')
    for id, slug in EXPORTTEMPLATE_LANGUAGE_CHOICES:
        ExportTemplate.objects.filter(template_language=str(id)).update(template_language=slug)


def webhook_contenttype_to_slug(apps, schema_editor):
    Webhook = apps.get_model('extras', 'Webhook')
    for id, slug in WEBHOOK_CONTENTTYPE_CHOICES:
        Webhook.objects.filter(http_content_type=str(id)).update(http_content_type=slug)


def graph_type_to_fk(apps, schema_editor):
    Graph = apps.get_model('extras', 'Graph')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    # On a new installation (and during tests) content types might not yet exist. So, we only perform the bulk
    # updates if a Graph has been created, which implies that we're working with a populated database.
    if Graph.objects.exists():
        for id, app_label, model in GRAPH_TYPE_CHOICES:
            content_type = ContentType.objects.get(app_label=app_label, model=model)
            Graph.objects.filter(type=id).update(type=content_type.pk)


class Migration(migrations.Migration):

    replaces = [('extras', '0022_custom_links'), ('extras', '0023_fix_tag_sequences'), ('extras', '0024_scripts'), ('extras', '0025_objectchange_time_index'), ('extras', '0026_webhook_ca_file_path'), ('extras', '0027_webhook_additional_headers'), ('extras', '0028_remove_topology_maps'), ('extras', '0029_3569_customfield_fields'), ('extras', '0030_3569_objectchange_fields'), ('extras', '0031_3569_exporttemplate_fields'), ('extras', '0032_3569_webhook_fields'), ('extras', '0033_graph_type_template_language'), ('extras', '0034_configcontext_tags')]

    dependencies = [
        ('extras', '0021_add_color_comments_changelog_to_tag'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('text', models.CharField(max_length=500)),
                ('url', models.CharField(max_length=500)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('group_name', models.CharField(blank=True, max_length=50)),
                ('button_class', models.CharField(default='default', max_length=30)),
                ('new_window', models.BooleanField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['group_name', 'weight', 'name'],
            },
        ),
        migrations.AlterField(
            model_name='customfield',
            name='obj_type',
            field=models.ManyToManyField(related_name='custom_fields', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='obj_type',
            field=models.ManyToManyField(related_name='webhooks', to='contenttypes.ContentType'),
        ),
        migrations.RunSQL(
            sql="SELECT setval('extras_tag_id_seq', (SELECT id FROM extras_tag ORDER BY id DESC LIMIT 1) + 1)",
        ),
        migrations.RunSQL(
            sql="SELECT setval('extras_taggeditem_id_seq', (SELECT id FROM extras_taggeditem ORDER BY id DESC LIMIT 1) + 1)",
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'permissions': (('run_script', 'Can run script'),),
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AddField(
            model_name='webhook',
            name='ca_file_path',
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
        migrations.AddField(
            model_name='webhook',
            name='additional_headers',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='TopologyMap',
        ),
        migrations.AlterField(
            model_name='customfield',
            name='type',
            field=models.CharField(default='text', max_length=50),
        ),
        migrations.RunPython(
            code=customfield_type_to_slug,
        ),
        migrations.AlterField(
            model_name='customfieldchoice',
            name='field',
            field=models.ForeignKey(limit_choices_to={'type': 'select'}, on_delete=django.db.models.deletion.CASCADE, related_name='choices', to='extras.CustomField'),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='filter_logic',
            field=models.CharField(default='loose', max_length=50),
        ),
        migrations.RunPython(
            code=customfield_filter_logic_to_slug,
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='action',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=objectchange_action_to_slug,
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='template_language',
            field=models.CharField(default='jinja2', max_length=50),
        ),
        migrations.RunPython(
            code=exporttemplate_language_to_slug,
        ),
        migrations.AlterField(
            model_name='webhook',
            name='http_content_type',
            field=models.CharField(default='application/json', max_length=50),
        ),
        migrations.RunPython(
            code=webhook_contenttype_to_slug,
        ),
        migrations.RunPython(
            code=graph_type_to_fk,
        ),
        migrations.AlterField(
            model_name='graph',
            name='type',
            field=models.ForeignKey(limit_choices_to={'model__in': ['provider', 'device', 'interface', 'site']}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='graph',
            name='template_language',
            field=models.CharField(default='jinja2', max_length=50),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='_configcontext_tags_+', to='extras.Tag'),
        ),
    ]
