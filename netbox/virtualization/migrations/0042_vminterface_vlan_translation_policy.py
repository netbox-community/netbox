import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0074_vlantranslationpolicy_vlantranslationrule'),
        ('virtualization', '0041_charfield_null_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
            name='vlan_translation_policy',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlantranslationpolicy'
            ),
        ),
    ]
