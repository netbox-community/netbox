from django.db import migrations, models
import utilities.validators


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0006_created_datetimefield'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='link',
            field=models.URLField(blank=True),
        ),
    ]
