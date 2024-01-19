from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_initial'),
    ]

    replaces = [
        ('core', '0002_managedfile'),
        ('core', '0003_job'),
        ('core', '0004_replicate_jobresults'),
        ('core', '0005_job_created_auto_now'),
    ]

    operations = [
        migrations.AddField(
            model_name='datasource',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='datafile',
            name='source',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='datafiles', to='core.datasource'),
        ),
        migrations.AddField(
            model_name='autosyncrecord',
            name='datafile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.datafile'),
        ),
        migrations.AddField(
            model_name='autosyncrecord',
            name='object_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddIndex(
            model_name='managedfile',
            index=models.Index(fields=['file_root', 'file_path'], name='core_managedfile_root_path'),
        ),
        migrations.AddConstraint(
            model_name='managedfile',
            constraint=models.UniqueConstraint(fields=('file_root', 'file_path'), name='core_managedfile_unique_root_path'),
        ),
        migrations.AddIndex(
            model_name='datafile',
            index=models.Index(fields=['source', 'path'], name='core_datafile_source_path'),
        ),
        migrations.AddConstraint(
            model_name='datafile',
            constraint=models.UniqueConstraint(fields=('source', 'path'), name='core_datafile_unique_source_path'),
        ),
        migrations.AddIndex(
            model_name='autosyncrecord',
            index=models.Index(fields=['object_type', 'object_id'], name='core_autosy_object__c17bac_idx'),
        ),
        migrations.AddConstraint(
            model_name='autosyncrecord',
            constraint=models.UniqueConstraint(fields=('object_type', 'object_id'), name='core_autosyncrecord_object'),
        ),
    ]
