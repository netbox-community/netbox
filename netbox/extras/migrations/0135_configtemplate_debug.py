from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0134_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='configtemplate',
            name='debug',
            field=models.BooleanField(
                default=False,
                help_text=(
                    'Enable verbose error output when rendering this template. '
                    'Not recommended for production use.'
                ),
                verbose_name='debug',
            ),
        ),
    ]
