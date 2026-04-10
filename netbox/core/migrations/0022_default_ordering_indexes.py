from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0021_job_queue_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='configrevision',
            index=models.Index(fields=['-created'], name='core_config_created_ef9552_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['-created'], name='core_job_created_efa7cb_idx'),
        ),
    ]
