from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0099_populate_prefix_classification'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='prefix',
            index=models.Index(fields=['_classification'], name='ipam_prefix_classification_idx'),
        ),
    ]
