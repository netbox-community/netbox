import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0239_add_portmapping_objectchange'),
        ('ipam', '0092_iprange_host_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prefix',
            name='_region',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.region'
            ),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='_site_group',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dcim.sitegroup'
            ),
        ),
    ]
