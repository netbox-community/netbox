from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('tenancy', '0025_ltree_paths'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='tenant',
            name='tenancy_tenant_unique_group_name',
        ),
        migrations.RemoveConstraint(
            model_name='tenant',
            name='tenancy_tenant_unique_name',
        ),
        migrations.RemoveConstraint(
            model_name='tenant',
            name='tenancy_tenant_unique_group_slug',
        ),
        migrations.RemoveConstraint(
            model_name='tenant',
            name='tenancy_tenant_unique_slug',
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                fields=('group', 'name'),
                name='tenancy_tenant_unique_group_name',
                nulls_distinct=False,
                violation_error_message='Tenant name must be unique per group.',
            ),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                fields=('group', 'slug'),
                name='tenancy_tenant_unique_group_slug',
                nulls_distinct=False,
                violation_error_message='Tenant slug must be unique per group.',
            ),
        ),
    ]
