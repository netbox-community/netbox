from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0232_default_ordering_indexes'),
        ('extras', '0137_default_ordering_indexes'),
        ('ipam', '0089_default_ordering_indexes'),
        ('tenancy', '0024_default_ordering_indexes'),
        ('users', '0016_default_ordering_indexes'),
        ('wireless', '0018_add_mptt_tree_indexes'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='wirelesslan',
            index=models.Index(fields=['ssid', 'id'], name='wireless_wi_ssid_64a9ce_idx'),
        ),
    ]
