import utilities.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0215_rackreservation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
    ]
