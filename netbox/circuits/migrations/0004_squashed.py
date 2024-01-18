from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('circuits', '0003_squashed'),
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
        ('circuits', '0003_extend_tag_support'),  # Misnumbered
        ('circuits', '0004_rename_cable_peer'),   # Misnumbered
        ('circuits', '0032_provider_service_id'),
        ('circuits', '0033_standardize_id_fields'),
        ('circuits', '0034_created_datetimefield'),
        ('circuits', '0035_provider_asns'),
        ('circuits', '0036_circuit_termination_date_tags_custom_fields'),
        ('circuits', '0037_new_cabling_models'),
        ('circuits', '0038_cabling_cleanup'),
        ('circuits', '0039_unique_constraints'),
        ('circuits', '0040_provider_remove_deprecated_fields'),
        ('circuits', '0041_standardize_description_comments'),
        ('circuits', '0042_provideraccount'),
    ]

    operations = [
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
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_providernetwork_unique_provider_name'),
        ),
        migrations.AddConstraint(
            model_name='provideraccount',
            constraint=models.UniqueConstraint(fields=('provider', 'account'), name='circuits_provideraccount_unique_provider_account'),
        ),
        migrations.AddConstraint(
            model_name='provideraccount',
            constraint=models.UniqueConstraint(condition=models.Q(('name', ''), _negated=True), fields=('provider', 'name'), name='circuits_provideraccount_unique_provider_name'),
        ),
        migrations.AddConstraint(
            model_name='circuittermination',
            constraint=models.UniqueConstraint(fields=('circuit', 'term_side'), name='circuits_circuittermination_unique_circuit_term_side'),
        ),
        migrations.AddConstraint(
            model_name='circuit',
            constraint=models.UniqueConstraint(fields=('provider', 'cid'), name='circuits_circuit_unique_provider_cid'),
        ),
        migrations.AddConstraint(
            model_name='circuit',
            constraint=models.UniqueConstraint(fields=('provider_account', 'cid'), name='circuits_circuit_unique_provideraccount_cid'),
        ),
    ]
