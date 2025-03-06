import django.db.models.deletion
import mptt.fields
import taggit.managers
from django.db import migrations, models

import utilities.json
import wireless.models


class Migration(migrations.Migration):
    replaces = [
        ('wireless', '0001_wireless'),
        ('wireless', '0002_standardize_id_fields'),
        ('wireless', '0003_created_datetimefield'),
        ('wireless', '0004_wireless_tenancy'),
        ('wireless', '0005_wirelesslink_interface_types'),
        ('wireless', '0006_unique_constraints'),
        ('wireless', '0007_standardize_description_comments'),
        ('wireless', '0008_wirelesslan_status'),
    ]

    dependencies = [
        ('ipam', '0002_squashed_0046'),
        ('tenancy', '0007_contact_link'),
        ('extras', '0002_squashed_0059'),
        ('dcim', '0003_squashed_0130'),
    ]

    operations = [
        migrations.CreateModel(
            name='WirelessLANGroup',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                (
                    'parent',
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='children',
                        to='wireless.wirelesslangroup',
                    ),
                ),
            ],
            options={
                'ordering': ('name', 'pk'),
                'unique_together': set(),
                'verbose_name': 'Wireless LAN Group',
            },
        ),
        migrations.CreateModel(
            name='WirelessLAN',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('ssid', models.CharField(max_length=32)),
                (
                    'group',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='wireless_lans',
                        to='wireless.wirelesslangroup',
                    ),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('auth_cipher', models.CharField(blank=True, max_length=50)),
                ('auth_psk', models.CharField(blank=True, max_length=64)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'vlan',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlan'
                    ),
                ),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='wireless_lans',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Wireless LAN',
                'ordering': ('ssid', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='WirelessLink',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('ssid', models.CharField(blank=True, max_length=32)),
                ('status', models.CharField(default='connected', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('auth_cipher', models.CharField(blank=True, max_length=50)),
                ('auth_psk', models.CharField(blank=True, max_length=64)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                (
                    '_interface_a_device',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='+',
                        to='dcim.device',
                    ),
                ),
                (
                    '_interface_b_device',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='+',
                        to='dcim.device',
                    ),
                ),
                (
                    'interface_a',
                    models.ForeignKey(
                        limit_choices_to=wireless.models.get_wireless_interface_types,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='dcim.interface',
                    ),
                ),
                (
                    'interface_b',
                    models.ForeignKey(
                        limit_choices_to=wireless.models.get_wireless_interface_types,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='dcim.interface',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='wireless_links',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'ordering': ['pk'],
                'unique_together': set(),
            },
        ),
        migrations.AddConstraint(
            model_name='wirelesslangroup',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'), name='wireless_wirelesslangroup_unique_parent_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='wirelesslink',
            constraint=models.UniqueConstraint(
                fields=('interface_a', 'interface_b'), name='wireless_wirelesslink_unique_interfaces'
            ),
        ),
        migrations.AddField(
            model_name='wirelesslan',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='wirelesslink',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='wirelesslan',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
    ]
