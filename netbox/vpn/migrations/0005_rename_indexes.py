from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0004_alter_ikepolicy_mode'),
    ]

    operations = [

        # Rename vpn_l2vpn constraints
        migrations.RunSQL("ALTER TABLE vpn_l2vpn RENAME CONSTRAINT ipam_l2vpn_tenant_id_bb2564a6_fk_tenancy_tenant_id TO vpn_l2vpn_tenant_id_57ec8f92_fk_tenancy_tenant_id"),

        # Rename ipam_l2vpn_* sequences
        migrations.RunSQL("ALTER TABLE ipam_l2vpn_export_targets_id_seq RENAME TO vpn_l2vpn_export_targets_id_seq"),
        migrations.RunSQL("ALTER TABLE ipam_l2vpn_id_seq RENAME TO vpn_l2vpn_id_seq"),
        migrations.RunSQL("ALTER TABLE ipam_l2vpn_import_targets_id_seq RENAME TO vpn_l2vpn_import_targets_id_seq"),

        # Rename ipam_l2vpn_* indexes
        migrations.RunSQL("ALTER INDEX ipam_l2vpn_pkey RENAME TO vpn_l2vpn_pkey"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpn_name_5e1c080f_like RENAME TO vpn_l2vpn_name_8824eda5_like"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpn_name_key RENAME TO vpn_l2vpn_name_key"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpn_slug_24008406_like RENAME TO vpn_l2vpn_slug_76b5a174_like"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpn_tenant_id_bb2564a6 RENAME TO vpn_l2vpn_tenant_id_57ec8f92"),
        # The unique index for L2VPN.slug may have one of two names, depending on how it was created,
        # so we check for both.
        migrations.RunSQL("ALTER INDEX IF EXISTS ipam_l2vpn_slug_24008406_uniq RENAME TO vpn_l2vpn_slug_76b5a174_uniq"),
        migrations.RunSQL("ALTER INDEX IF EXISTS ipam_l2vpn_slug_key RENAME TO vpn_l2vpn_slug_key"),

        # Rename vpn_l2vpntermination constraints
        migrations.RunSQL("ALTER TABLE vpn_l2vpntermination RENAME CONSTRAINT ipam_l2vpntermination_assigned_object_id_check TO vpn_l2vpntermination_assigned_object_id_check"),
        migrations.RunSQL("ALTER TABLE vpn_l2vpntermination RENAME CONSTRAINT ipam_l2vpnterminatio_assigned_object_type_3923c124_fk_django_co TO vpn_l2vpntermination_assigned_object_type_id_f063b865_fk_django_co"),
        migrations.RunSQL("ALTER TABLE vpn_l2vpntermination RENAME CONSTRAINT ipam_l2vpntermination_l2vpn_id_9e570aa1_fk_ipam_l2vpn_id TO vpn_l2vpntermination_l2vpn_id_f5367bbe_fk_vpn_l2vpn_id"),

        # Rename ipam_l2vpn_termination_* sequences
        migrations.RunSQL("ALTER TABLE ipam_l2vpntermination_id_seq RENAME TO vpn_l2vpntermination_id_seq"),

        # Rename ipam_l2vpn_* indexes
        migrations.RunSQL("ALTER INDEX ipam_l2vpntermination_pkey RENAME TO vpn_l2vpntermination_pkey"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpntermination_assigned_object_type_id_3923c124 RENAME TO vpn_l2vpntermination_assigned_object_type_id_f063b865"),
        migrations.RunSQL("ALTER INDEX ipam_l2vpntermination_l2vpn_id_9e570aa1 RENAME TO vpn_l2vpntermination_l2vpn_id_f5367bbe"),

    ]
