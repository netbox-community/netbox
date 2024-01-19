from django.db import migrations
import utilities.fields


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0042_provideraccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittype',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
    ]
