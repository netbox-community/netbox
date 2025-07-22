import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0017_concrete_objecttype'),
        ('extras', '0130_imageattachment_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='Tag',
            name='object_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='CustomField',
            name='related_object_type',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.objecttype'
            ),
        ),
        migrations.AlterField(
            model_name='CustomField',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_fields', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='EventRule',
            name='object_types',
            field=models.ManyToManyField(related_name='event_rules', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='CustomLink',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_links', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='ExportTemplate',
            name='object_types',
            field=models.ManyToManyField(related_name='export_templates', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='SavedFilter',
            name='object_types',
            field=models.ManyToManyField(related_name='saved_filters', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='TableConfig',
            name='object_type',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='table_configs', to='core.objecttype'
            ),
        ),
    ]
