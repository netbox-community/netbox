import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0193_poweroutlet_color'),
        ('ipam', '0070_vlangroup_vlan_id_ranges'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='dcim.location'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='dcim.region'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='site_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='dcim.sitegroup'),
        ),
    ]
