from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0077_customlink_extend_text_and_url'),
    ]

    operations = [
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
            constraint=models.UniqueConstraint(fields=('content_type', 'name'), name='extras_exporttemplate_unique_content_type_name'),
        ),
        migrations.AddConstraint(
            model_name='webhook',
            constraint=models.UniqueConstraint(fields=('payload_url', 'type_create', 'type_update', 'type_delete'), name='extras_webhook_unique_payload_url_types'),
        ),
    ]
