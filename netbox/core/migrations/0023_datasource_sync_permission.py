from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_default_ordering_indexes'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasource',
            options={'ordering': ('name',), 'permissions': [('sync', 'Synchronize data from remote source')]},
        ),
    ]
