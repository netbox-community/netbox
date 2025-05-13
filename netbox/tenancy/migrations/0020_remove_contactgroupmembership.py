from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0019_contactgroup_comments_tenantgroup_comments'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Remove the "through" models from the M2M field
                migrations.AlterField(
                    model_name='contact',
                    name='groups',
                    field=models.ManyToManyField(
                        blank=True,
                        related_name='contacts',
                        related_query_name='contact',
                        to='tenancy.contactgroup'
                    ),
                ),
                # Remove the ContactGroupMembership model
                migrations.DeleteModel(
                    name='ContactGroupMembership',
                ),
            ],
            database_operations=[
                # Rename ContactGroupMembership table
                migrations.AlterModelTable(
                    name='ContactGroupMembership',
                    table='tenancy_contact_groups',
                ),
                # Rename the 'group' column (also renames its FK constraint)
                migrations.RenameField(
                    model_name='contactgroupmembership',
                    old_name='group',
                    new_name='contactgroup',
                ),
                # Rename PK sequence
                migrations.RunSQL(
                    'ALTER TABLE tenancy_contactgroupmembership_id_seq '
                    'RENAME TO tenancy_contact_groups_id_seq'
                ),
                # Rename indexes
                migrations.RunSQL(
                    'ALTER INDEX tenancy_contactgroupmembership_pkey '
                    'RENAME TO tenancy_contact_groups_pkey'
                ),
                migrations.RunSQL(
                    'ALTER INDEX tenancy_contactgroupmembership_contact_id_04a138a7 '
                    'RENAME TO tenancy_contact_groups_contact_id_84c9d84f'
                ),
                migrations.RunSQL(
                    'ALTER INDEX tenancy_contactgroupmembership_group_id_bc712dd0 '
                    'RENAME TO tenancy_contact_groups_contactgroup_id_5c8d6c5a'
                ),
                migrations.RunSQL(
                    'ALTER INDEX unique_group_name '
                    'RENAME TO tenancy_contact_groups_contact_id_contactgroup_id_f4434f2c_uniq'
                ),
                # Rename foreign key constraint for contact_id
                migrations.RunSQL(
                    'ALTER TABLE tenancy_contact_groups '
                    'RENAME CONSTRAINT tenancy_contactgroup_contact_id_04a138a7_fk_tenancy_c '
                    'TO tenancy_contact_grou_contact_id_84c9d84f_fk_tenancy_c'
                ),
            ],
        ),
    ]
