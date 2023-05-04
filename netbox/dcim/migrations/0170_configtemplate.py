from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0086_configtemplate'),
        ('dcim', '0169_devicetype_default_platform'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='config_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='devices', to='extras.configtemplate'),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='config_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='device_roles', to='extras.configtemplate'),
        ),
        migrations.AddField(
            model_name='platform',
            name='config_template',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='platforms', to='extras.configtemplate'),
        ),
    ]
