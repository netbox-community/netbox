from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_objectpermission_update_object_types'),
    ]

    operations = [
        # Flip M2M assignments for ObjectPermission to Groups
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='objectpermission',
                    name='groups',
                ),
                migrations.AddField(
                    model_name='group',
                    name='object_permissions',
                    field=models.ManyToManyField(blank=True, related_name='groups', to='users.objectpermission'),
                ),
            ],
            database_operations=[
                # Rename table
                migrations.RunSQL(
                    "ALTER TABLE users_objectpermission_groups"
                    "  RENAME TO users_group_object_permissions"
                ),
                migrations.RunSQL(
                    "ALTER TABLE users_objectpermission_groups_id_seq"
                    "  RENAME TO users_group_object_permissions_id_seq"
                ),

                # Rename constraints
                migrations.RunSQL(
                    "ALTER TABLE users_group_object_permissions RENAME CONSTRAINT "
                    "users_objectpermissi_group_id_fb7ba6e0_fk_users_gro TO "
                    "users_group_object_p_group_id_90dd183a_fk_users_gro"
                ),
                migrations.RunSQL(
                    "ALTER TABLE users_group_object_permissions RENAME CONSTRAINT "
                    "users_objectpermissi_objectpermission_id_2f7cc117_fk_users_obj TO "
                    "users_group_object_p_objectpermission_id_dd489dc4_fk_users_obj"
                ),

                # Rename indexes
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_groups_pkey "
                    "  RENAME TO users_group_object_permissions_pkey"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_g_objectpermission_id_grou_3b62a39c_uniq "
                    "  RENAME TO users_group_object_permi_group_id_objectpermissio_db1f8cbe_uniq"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_groups_group_id_fb7ba6e0"
                    "  RENAME TO users_group_object_permissions_group_id_90dd183a"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_groups_objectpermission_id_2f7cc117"
                    "  RENAME TO users_group_object_permissions_objectpermission_id_dd489dc4"
                ),
            ]
        ),

        # Flip M2M assignments for ObjectPermission to Users
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.RemoveField(
                    model_name='objectpermission',
                    name='users',
                ),
                migrations.AddField(
                    model_name='user',
                    name='object_permissions',
                    field=models.ManyToManyField(blank=True, related_name='users', to='users.objectpermission'),
                ),
            ],
            database_operations=[
                # Rename table
                migrations.RunSQL(
                    "ALTER TABLE users_objectpermission_users"
                    "  RENAME TO users_user_object_permissions"
                ),
                migrations.RunSQL(
                    "ALTER TABLE users_objectpermission_users_id_seq"
                    "  RENAME TO users_user_object_permissions_id_seq"
                ),

                # Rename constraints
                migrations.RunSQL(
                    "ALTER TABLE users_user_object_permissions RENAME CONSTRAINT "
                    "users_objectpermissi_objectpermission_id_78a9c2e6_fk_users_obj TO "
                    "users_user_object_pe_objectpermission_id_29b431b4_fk_users_obj"
                ),
                migrations.RunSQL(
                    "ALTER TABLE users_user_object_permissions RENAME CONSTRAINT "
                    "users_objectpermission_users_user_id_16c0905d_fk_auth_user_id TO "
                    "users_user_object_permissions_user_id_9d647aac_fk_users_user_id"
                ),

                # Rename indexes
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_users_pkey "
                    "  RENAME TO users_user_object_permissions_pkey"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_u_objectpermission_id_user_3a7db108_uniq "
                    "  RENAME TO users_user_object_permis_user_id_objectpermission_0a98550e_uniq"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_users_user_id_16c0905d"
                    "  RENAME TO users_user_object_permissions_user_id_9d647aac"
                ),
                migrations.RunSQL(
                    "ALTER INDEX users_objectpermission_users_objectpermission_id_78a9c2e6"
                    "  RENAME TO users_user_object_permissions_objectpermission_id_29b431b4"
                ),
            ]
        ),
    ]
