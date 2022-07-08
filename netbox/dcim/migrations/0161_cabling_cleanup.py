from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0160_populate_cable_ends'),
    ]

    operations = [

        # Remove old fields from Cable
        migrations.AlterModelOptions(
            name='cable',
            options={'ordering': ('pk',)},
        ),
        migrations.AlterUniqueTogether(
            name='cable',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_a_id',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_a_type',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_b_id',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='termination_b_type',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='_termination_a_device',
        ),
        migrations.RemoveField(
            model_name='cable',
            name='_termination_b_device',
        ),

        # Remove old fields from CablePath
        migrations.AlterUniqueTogether(
            name='cablepath',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='destination_id',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='destination_type',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='origin_id',
        ),
        migrations.RemoveField(
            model_name='cablepath',
            name='origin_type',
        ),

        # Remove link peer type/ID fields from cable termination models
        migrations.RemoveField(
            model_name='consoleport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_link_peer_type',
        ),
        migrations.RemoveField(
            model_name='rearport',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='rearport',
            name='_link_peer_type',
        ),

    ]
