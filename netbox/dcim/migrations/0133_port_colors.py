from django.db import migrations
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0132_cable_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontport',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='rearport',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='color',
            field=utilities.fields.ColorField(blank=True, max_length=6),
        ),
    ]
