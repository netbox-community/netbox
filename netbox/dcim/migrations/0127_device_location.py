from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0126_rename_rackgroup_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='dcim.location'),
        ),
    ]
