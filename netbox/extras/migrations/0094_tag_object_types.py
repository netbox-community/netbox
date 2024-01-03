from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0093_configrevision_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='object_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.RenameIndex(
            model_name='taggeditem',
            new_name='extras_tagg_content_717743_idx',
            old_fields=('content_type', 'object_id'),
        ),
    ]
