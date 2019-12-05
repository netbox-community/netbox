from django.db import migrations, models


WEBHOOK_CONTENTTYPE_CHOICES = (
    (1, 'application/json'),
    (2, 'application/x-www-form-urlencoded'),
)


def webhook_contenttype_to_slug(apps, schema_editor):
    Webhook = apps.get_model('extras', 'Webhook')
    for id, slug in WEBHOOK_CONTENTTYPE_CHOICES:
        Webhook.objects.filter(http_content_type=str(id)).update(http_content_type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('extras', '0031_3569_exporttemplate_fields'),
    ]

    operations = [

        # Webhook.http_content_type
        migrations.AlterField(
            model_name='webhook',
            name='http_content_type',
            field=models.CharField(default='application/json', max_length=50),
        ),
        migrations.RunPython(
            code=webhook_contenttype_to_slug
        ),

    ]
