from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0156_location_status'),
    ]

    operations = [

        # Create CableTermination model
        migrations.CreateModel(
            name='CableTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('cable_end', models.CharField(max_length=1)),
                ('termination_id', models.PositiveBigIntegerField()),
                ('cable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='dcim.cable')),
                ('termination_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ('circuittermination',))), models.Q(('app_label', 'dcim'), ('model__in', ('consoleport', 'consoleserverport', 'frontport', 'interface', 'powerfeed', 'poweroutlet', 'powerport', 'rearport'))), _connector='OR')), on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.device')),
                ('_rack', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.rack')),
                ('_location', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.location')),
                ('_site', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dcim.site')),
            ],
            options={
                'ordering': ('cable', 'cable_end', 'pk'),
            },
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(fields=('termination_type', 'termination_id'), name='dcim_cable_termination_unique_termination'),
        ),

        # Update CablePath model
        migrations.RenameField(
            model_name='cablepath',
            old_name='path',
            new_name='_nodes',
        ),
        migrations.AddField(
            model_name='cablepath',
            name='path',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='cablepath',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),

        # Add cable_end field to cable termination models
        migrations.AddField(
            model_name='consoleport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='frontport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='interface',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='powerport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
        migrations.AddField(
            model_name='rearport',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]
