from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0137_default_ordering_indexes'),
        ('ipam', '0089_default_ordering_indexes'),
        ('vpn', '0011_add_comments_to_organizationalmodel'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='tunneltermination',
            index=models.Index(fields=['tunnel', 'role', 'id'], name='vpn_tunnelt_tunnel__f542d3_idx'),
        ),
    ]
