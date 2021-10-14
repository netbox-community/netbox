from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0002_squashed_0029'),
    ]

    operations = [
        migrations.RenameField(
            model_name='circuittermination',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='circuittermination',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
    ]
