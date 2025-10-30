import utilities.fields
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0217_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='devicetype',
            name='device_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='device_type', to_model='dcim.Device'
            ),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='module_count',
            field=utilities.fields.CounterCacheField(
                default=0, editable=False, to_field='module_type', to_model='dcim.Module'
            ),
        ),
    ]
