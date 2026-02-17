from django.db import migrations

import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0216_latitude_longitude_validators'),
    ]

    operations = [
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
    ]
