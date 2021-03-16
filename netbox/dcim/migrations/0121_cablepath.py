import dcim.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0120_cache_cable_peer'),
    ]

    operations = [
        migrations.CreateModel(
            name='CablePath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('origin_id', models.PositiveIntegerField()),
                ('destination_id', models.PositiveIntegerField(blank=True, null=True)),
                ('path', dcim.fields.PathField(base_field=models.CharField(max_length=40), size=None)),
                ('is_active', models.BooleanField(default=False)),
                ('is_split', models.BooleanField(default=False)),
                ('destination_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
                ('origin_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'unique_together': {('origin_type', 'origin_id')},
            },
        ),
        migrations.AddField(
            model_name='consoleport',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='interface',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='_path',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.cablepath'),
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='connected_endpoint',
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='connection_status',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='connection_status',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_connected_circuittermination',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='_connected_interface',
        ),
        migrations.RemoveField(
            model_name='interface',
            name='connection_status',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='connected_endpoint',
        ),
        migrations.RemoveField(
            model_name='powerfeed',
            name='connection_status',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='connection_status',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_connected_powerfeed',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_connected_poweroutlet',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='connection_status',
        ),
    ]
