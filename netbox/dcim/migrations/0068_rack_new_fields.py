from django.db import migrations, models

import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0067_device_type_remove_qualifiers'),
    ]

    operations = [
        migrations.AddField(
            model_name='rack',
            name='status',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='rack',
            name='asset_tag',
            field=utilities.fields.NullableCharField(blank=True, max_length=50, null=True, unique=True),
        ),
    ]
