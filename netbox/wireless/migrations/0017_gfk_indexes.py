from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0225_gfk_indexes'),
        ('extras', '0134_owner'),
        ('ipam', '0086_gfk_indexes'),
        ('tenancy', '0022_add_comments_to_organizationalmodel'),
        ('users', '0015_owner'),
        ('wireless', '0016_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='wirelesslan',
            index=models.Index(fields=['scope_type', 'scope_id'], name='wireless_wi_scope_t_6740a3_idx'),
        ),
    ]
