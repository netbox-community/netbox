from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0153_created_datetimefield'),
        ('virtualization', '0030_cluster_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='virtualmachine',
            name='device',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='dcim.device'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='virtual_machines', to='virtualization.cluster'),
        ),
    ]
