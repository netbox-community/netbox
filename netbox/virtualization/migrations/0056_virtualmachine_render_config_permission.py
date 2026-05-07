from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0055_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='virtualmachine',
            options={'ordering': ('name', 'pk'), 'permissions': [('render_config', 'Render configuration')]},
        ),
    ]
