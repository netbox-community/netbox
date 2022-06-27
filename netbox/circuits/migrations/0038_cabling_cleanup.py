from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0037_new_cabling_models'),
        ('dcim', '0160_populate_cable_ends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circuittermination',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='circuittermination',
            name='_link_peer_type',
        ),
    ]
