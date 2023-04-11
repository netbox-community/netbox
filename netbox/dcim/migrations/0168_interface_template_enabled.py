from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0167_module_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='interfacetemplate',
            name='enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='bridge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bridge_interfaces', to='dcim.interfacetemplate'),
        ),
    ]
