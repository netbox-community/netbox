from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_datasource_sync_interval'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='autosyncrecord',
            name='core_autosy_object__c17bac_idx',
        ),
        migrations.RemoveIndex(
            model_name='datafile',
            name='core_datafile_source_path',
        ),
        migrations.RemoveIndex(
            model_name='managedfile',
            name='core_managedfile_root_path',
        ),
    ]
