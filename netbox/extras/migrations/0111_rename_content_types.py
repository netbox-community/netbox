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
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS extras_customfield_content_types_id_seq RENAME TO extras_customfield_object_types_id_seq"
        ),
        # Pre-v2.10 sequence name (see #15605)
        migrations.RunSQL(
            "ALTER TABLE IF EXISTS extras_customfield_obj_type_id_seq RENAME TO extras_customfield_object_types_id_seq"
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
        migrations.RunSQL(
            "ALTER TABLE extras_customlink_content_types_id_seq RENAME TO extras_customlink_object_types_id_seq"
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
        migrations.RunSQL(
            "ALTER TABLE extras_eventrule_content_types_id_seq RENAME TO extras_eventrule_object_types_id_seq"
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
        migrations.RunSQL(
            "ALTER TABLE extras_exporttemplate_content_types_id_seq RENAME TO extras_exporttemplate_object_types_id_seq"
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
        migrations.RunSQL(
            "ALTER TABLE extras_savedfilter_content_types_id_seq RENAME TO extras_savedfilter_object_types_id_seq"
        ),

        # Image attachments
        migrations.RemoveIndex(
            model_name='imageattachment',
            name='extras_imag_content_94728e_idx',
        ),
        migrations.RenameField(
            model_name='imageattachment',
            old_name='content_type',
            new_name='object_type',
        ),
        migrations.AddIndex(
            model_name='imageattachment',
            index=models.Index(fields=['object_type', 'object_id'], name='extras_imag_object__96bebc_idx'),
        ),
    ]
