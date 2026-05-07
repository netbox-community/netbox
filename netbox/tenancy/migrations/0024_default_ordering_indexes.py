from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0137_default_ordering_indexes'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contact',
            index=models.Index(fields=['name'], name='tenancy_con_name_c26153_idx'),
        ),
        migrations.AddIndex(
            model_name='contactassignment',
            index=models.Index(fields=['contact', 'priority', 'role', 'id'], name='tenancy_con_contact_23011f_idx'),
        ),
    ]
