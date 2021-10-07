import dcim.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0133_port_colors'),
    ]

    operations = [
        migrations.AddField(
            model_name='interface',
            name='wwn',
            field=dcim.fields.WWNField(blank=True, null=True),
        ),
    ]
