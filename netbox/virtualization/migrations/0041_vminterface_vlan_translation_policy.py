# Generated by Django 5.0.9 on 2024-10-11 19:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0073_vlantranslationpolicy_vlantranslationrule'),
        ('virtualization', '0040_convert_disk_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='vminterface',
            name='vlan_translation_policy',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlantranslationpolicy'),
        ),
    ]