from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('circuits', '0001_initial'),
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    replaces = [
        ('circuits', '0002_auto_20160622_1821'),
        ('circuits', '0003_provider_32bit_asn_support'),
        ('circuits', '0004_circuit_add_tenant'),
        ('circuits', '0005_circuit_add_upstream_speed'),
        ('circuits', '0006_terminations'),
        ('circuits', '0007_circuit_add_description'),
        ('circuits', '0008_circuittermination_interface_protect_on_delete'),
        ('circuits', '0009_unicode_literals'),
        ('circuits', '0010_circuit_status'),
        ('circuits', '0011_tags'),
        ('circuits', '0012_change_logging'),
        ('circuits', '0013_cables'),
        ('circuits', '0014_circuittermination_description'),
        ('circuits', '0015_custom_tag_models'),
        ('circuits', '0016_3569_circuit_fields'),
        ('circuits', '0017_circuittype_description'),
        ('circuits', '0018_standardize_description'),
        ('circuits', '0019_nullbooleanfield_to_booleanfield'),
        ('circuits', '0020_custom_field_data'),
        ('circuits', '0021_cache_cable_peer'),
        ('circuits', '0022_cablepath'),
        ('circuits', '0023_circuittermination_port_speed_optional'),
        ('circuits', '0024_standardize_name_length'),
        ('circuits', '0025_standardize_models'),
        ('circuits', '0026_mark_connected'),
        ('circuits', '0027_providernetwork'),
        ('circuits', '0028_cache_circuit_terminations'),
        ('circuits', '0029_circuit_tracing'),
    ]

    operations = [
        migrations.AddField(
            model_name='providernetwork',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='circuit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='circuits.circuit'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='provider_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='circuits.providernetwork'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provider'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='termination_a',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='circuits.circuittermination'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='termination_z',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='circuits.circuittermination'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.circuittype'),
        ),
        migrations.AddConstraint(
            model_name='providernetwork',
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_providernetwork_provider_name'),
        ),
        migrations.AlterUniqueTogether(
            name='providernetwork',
            unique_together={('provider', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='circuittermination',
            unique_together={('circuit', 'term_side')},
        ),
        migrations.AlterUniqueTogether(
            name='circuit',
            unique_together={('provider', 'cid')},
        ),
    ]
