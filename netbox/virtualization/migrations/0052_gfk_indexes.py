from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0225_gfk_indexes'),
        ('extras', '0134_owner'),
        ('tenancy', '0022_add_comments_to_organizationalmodel'),
        ('users', '0015_owner'),
        ('virtualization', '0051_add_comments_to_organizationalmodel'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='cluster',
            index=models.Index(fields=['scope_type', 'scope_id'], name='virtualizat_scope_t_fb3b6e_idx'),
        ),
    ]
