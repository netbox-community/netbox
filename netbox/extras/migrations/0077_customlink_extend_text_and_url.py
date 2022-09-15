from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0076_tag_slug_unicode'),
    ]

    operations = [
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
    ]
