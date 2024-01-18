from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('ipam', '0001_initial'),
        ('dcim', '0001_initial'),
    ]

    replaces = [
        ('dcim', '0002_auto_20160622_1821'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualdevicecontext',
            name='primary_ip4',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress'),
        ),
        migrations.AddField(
            model_name='virtualdevicecontext',
            name='primary_ip6',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ipam.ipaddress'),
        ),
        migrations.AddField(
            model_name='virtualdevicecontext',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
