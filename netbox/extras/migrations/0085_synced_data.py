from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('extras', '0084_staging'),
    ]

    operations = [
        # ConfigContexts
        migrations.AddField(
            model_name='configcontext',
            name='data_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_path',
            field=models.CharField(blank=True, editable=False, max_length=1000),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource'),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='auto_sync_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='configcontext',
            name='data_synced',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
        # ExportTemplates
        migrations.AddField(
            model_name='exporttemplate',
            name='data_file',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='core.datafile'),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_path',
            field=models.CharField(blank=True, editable=False, max_length=1000),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='core.datasource'),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='auto_sync_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='data_synced',
            field=models.DateTimeField(blank=True, editable=False, null=True),
        ),
    ]
