import json

from django.db import migrations, models


def json_to_text(apps, schema_editor):
    """
    Convert a JSON representation of HTTP headers to key-value pairs (one header per line)
    """
    Webhook = apps.get_model('extras', 'Webhook')
    for webhook in Webhook.objects.exclude(additional_headers=''):
        data = json.loads(webhook.additional_headers)
        headers = ['{}: {}'.format(k, v) for k, v in data.items()]
        Webhook.objects.filter(pk=webhook.pk).update(additional_headers='\n'.join(headers))


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0037_configcontexts_clusters'),
    ]

    operations = [
        migrations.AddField(
            model_name='webhook',
            name='http_method',
            field=models.CharField(default='POST', max_length=30),
        ),
        migrations.AddField(
            model_name='webhook',
            name='body_template',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='additional_headers',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='webhook',
            name='http_content_type',
            field=models.CharField(default='application/json', max_length=100),
        ),
        migrations.RunPython(
            code=json_to_text
        ),
    ]
