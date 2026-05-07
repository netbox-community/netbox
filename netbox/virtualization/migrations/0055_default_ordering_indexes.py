from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0232_default_ordering_indexes'),
        ('extras', '0137_default_ordering_indexes'),
        ('ipam', '0089_default_ordering_indexes'),
        ('tenancy', '0024_default_ordering_indexes'),
        ('users', '0016_default_ordering_indexes'),
        ('virtualization', '0054_virtualmachinetype'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='virtualmachine',
            index=models.Index(fields=['name', 'id'], name='virtualizat_name_16033e_idx'),
        ),
        migrations.AddIndex(
            model_name='virtualmachinetype',
            index=models.Index(fields=['name'], name='virtualizat_name_6cff11_idx'),
        ),
    ]
