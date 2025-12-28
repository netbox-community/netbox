from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0055_add_comments_to_organizationalmodel'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0224_add_comments_to_organizationalmodel'),
        ('extras', '0134_owner'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='circuittermination',
            index=models.Index(fields=['termination_type', 'termination_id'], name='circuits_ci_termina_505dda_idx'),
        ),
    ]
