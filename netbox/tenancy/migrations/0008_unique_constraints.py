from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_contact_link'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contact',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='contactassignment',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='contactgroup',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='contact',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='tenancy_contact_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='contactassignment',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id', 'contact', 'role'), name='tenancy_contactassignment_unique_object_contact_role'),
        ),
        migrations.AddConstraint(
            model_name='contactgroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='tenancy_contactgroup_unique_parent_name'),
        ),
    ]
