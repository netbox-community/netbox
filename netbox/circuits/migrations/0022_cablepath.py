from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0121_cablepath'),
        ('circuits', '0021_cache_cable_peer'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittermination',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.RemoveField(
            model_name='circuittermination',
            name='connected_endpoint',
        ),
        migrations.RemoveField(
            model_name='circuittermination',
            name='connection_status',
        ),
    ]
