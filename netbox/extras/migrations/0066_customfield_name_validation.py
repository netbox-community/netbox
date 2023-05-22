import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0065_imageattachment_change_logging'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='name',
            field=models.CharField(
                max_length=50,
                unique=True,
                validators=[
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        message='Only alphanumeric characters and underscores are allowed.',
                        regex='^[a-z0-9_]+$',
                    ),
                    django.core.validators.RegexValidator(
                        flags=re.RegexFlag['IGNORECASE'],
                        inverse_match=True,
                        message='Double underscores are not permitted in custom field names.',
                        regex=r'__',
                    ),
                ],
            ),
        ),
    ]
