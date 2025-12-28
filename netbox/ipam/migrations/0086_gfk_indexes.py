from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0225_gfk_indexes'),
        ('extras', '0134_owner'),
        ('ipam', '0085_add_comments_to_organizationalmodel'),
        ('tenancy', '0022_add_comments_to_organizationalmodel'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='prefix',
            index=models.Index(fields=['scope_type', 'scope_id'], name='ipam_prefix_scope_t_fe84a6_idx'),
        ),
    ]
