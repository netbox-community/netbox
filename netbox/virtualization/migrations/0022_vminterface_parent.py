from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('virtualization', '0021_virtualmachine_vcpus_decimal'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_interfaces', to='virtualization.vminterface'),
        ),
    ]
