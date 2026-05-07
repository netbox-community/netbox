from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0232_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ('name', 'pk'), 'permissions': [('render_config', 'Render configuration')]},
        ),
    ]
