from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='objectpermission',
            index=models.Index(fields=['name'], name='users_objec_name_ca707b_idx'),
        ),
        migrations.AddIndex(
            model_name='token',
            index=models.Index(fields=['-created'], name='users_token_created_1467b4_idx'),
        ),
    ]
