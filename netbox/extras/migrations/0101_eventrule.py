import django.db.models.deletion
import taggit.managers
from django.contrib.contenttypes.models import ContentType
from django.db import migrations, models

import utilities.json
from extras.choices import *


def move_webhooks(apps, schema_editor):
    Webhook = apps.get_model("extras", "Webhook")
    EventRule = apps.get_model("extras", "EventRule")

    webhook_ct = ContentType.objects.get_for_model(Webhook).pk
    for webhook in Webhook.objects.all():
        event = EventRule()

        # Replicate attributes from Webhook instance
        event.name = webhook.name
        event.type_create = webhook.type_create
        event.type_update = webhook.type_update
        event.type_delete = webhook.type_delete
        event.type_job_start = webhook.type_job_start
        event.type_job_end = webhook.type_job_end
        event.enabled = webhook.enabled
        event.conditions = webhook.conditions

        event.action_type = EventRuleActionChoices.WEBHOOK
        event.action_object_type_id = webhook_ct
        event.action_object_id = webhook.id
        event.save()
        event.content_types.add(*webhook.content_types.all())


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0100_customfield_ui_attrs'),
    ]

    operations = [

        # Create the EventRule model
        migrations.CreateModel(
            name='EventRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(max_length=150, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('type_create', models.BooleanField(default=False)),
                ('type_update', models.BooleanField(default=False)),
                ('type_delete', models.BooleanField(default=False)),
                ('type_job_start', models.BooleanField(default=False)),
                ('type_job_end', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
                ('conditions', models.JSONField(blank=True, null=True)),
                ('action_type', models.CharField(default='webhook', max_length=30)),
                ('action_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                ('action_parameters', models.JSONField(blank=True, null=True)),
                ('action_data', models.JSONField(blank=True, null=True)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'eventrule',
                'verbose_name_plural': 'eventrules',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='eventrule',
            name='action_object_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='eventrule_actions',
                to='contenttypes.contenttype',
            ),
        ),
        migrations.AddField(
            model_name='eventrule',
            name='content_types',
            field=models.ManyToManyField(related_name='eventrules', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='eventrule',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddIndex(
            model_name='eventrule',
            index=models.Index(fields=['action_object_type', 'action_object_id'], name='extras_even_action__d9e2af_idx'),
        ),

        # Replicate Webhook data
        migrations.RunPython(move_webhooks),

        # Remove obsolete fields from Webhook
        migrations.RemoveConstraint(
            model_name='webhook',
            name='extras_webhook_unique_payload_url_types',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='conditions',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='content_types',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='enabled',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='type_create',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='type_delete',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='type_job_end',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='type_job_start',
        ),
        migrations.RemoveField(
            model_name='webhook',
            name='type_update',
        ),

        # Add description field to Webhook
        migrations.AddField(
            model_name='webhook',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
