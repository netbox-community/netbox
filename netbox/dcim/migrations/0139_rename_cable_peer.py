from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0138_extend_tag_support'),
    ]

    operations = [
        migrations.RenameField(
            model_name='consoleport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='consoleport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='consoleserverport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='consoleserverport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='frontport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='frontport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='interface',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='powerfeed',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='powerfeed',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='poweroutlet',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='poweroutlet',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.RenameField(
            model_name='rearport',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='rearport',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
    ]
