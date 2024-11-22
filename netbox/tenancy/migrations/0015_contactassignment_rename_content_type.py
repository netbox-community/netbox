from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0111_rename_content_types'),
        ('tenancy', '0014_contactassignment_ordering'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='contactassignment',
            name='tenancy_contactassignment_unique_object_contact_role',
        ),
        migrations.RemoveIndex(
            model_name='contactassignment',
            name='tenancy_con_content_693ff4_idx',
        ),
        migrations.RenameField(
            model_name='contactassignment',
            old_name='content_type',
            new_name='object_type',
        ),
        migrations.AddIndex(
            model_name='contactassignment',
            index=models.Index(fields=['object_type', 'object_id'], name='tenancy_con_object__6f20f7_idx'),
        ),
        migrations.AddConstraint(
            model_name='contactassignment',
            constraint=models.UniqueConstraint(
                fields=('object_type', 'object_id', 'contact', 'role'),
                name='tenancy_contactassignment_unique_object_contact_role',
            ),
        ),
    ]
