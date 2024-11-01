from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0045_clusters_cached_relations'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vminterface',
            old_name='mac_address',
            new_name='_mac_address',
        ),
    ]
