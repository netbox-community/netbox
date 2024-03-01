import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_gfk_indexes'),
        ('extras', '0110_remove_eventrule_action_parameters'),
    ]

    operations = [
        # Custom fields
        migrations.RenameField(
            model_name='customfield',
            old_name='content_types',
            new_name='object_types',
        ),
        migrations.AlterField(
            model_name='customfield',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_fields', to='core.objecttype'),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='object_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='core.objecttype'),
        ),

        # Custom links
        migrations.RenameField(
            model_name='customlink',
            old_name='content_types',
            new_name='object_types',
        ),
        migrations.AlterField(
            model_name='customlink',
            name='object_types',
            field=models.ManyToManyField(related_name='custom_links', to='core.objecttype'),
        ),

        # Event rules
        migrations.RenameField(
            model_name='eventrule',
            old_name='content_types',
            new_name='object_types',
        ),
        migrations.AlterField(
            model_name='eventrule',
            name='object_types',
            field=models.ManyToManyField(related_name='event_rules', to='core.objecttype'),
        ),

        # Export templates
        migrations.RenameField(
            model_name='exporttemplate',
            old_name='content_types',
            new_name='object_types',
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='object_types',
            field=models.ManyToManyField(related_name='export_templates', to='core.objecttype'),
        ),

        # Saved filters
        migrations.RenameField(
            model_name='savedfilter',
            old_name='content_types',
            new_name='object_types',
        ),
        migrations.AlterField(
            model_name='savedfilter',
            name='object_types',
            field=models.ManyToManyField(related_name='saved_filters', to='core.objecttype'),
        ),
    ]
