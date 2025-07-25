from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0130_imageattachment_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_fields', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_links', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='eventrule',
            name='object_types',
            field=models.ManyToManyField(related_name='event_rules', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='object_types',
            field=models.ManyToManyField(related_name='export_templates', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='savedfilter',
            name='object_types',
            field=models.ManyToManyField(related_name='saved_filters', to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='object_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='contenttypes.contenttype'),
        ),
    ]
