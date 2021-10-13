import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0136_wireless'),
        ('extras', '0062_clear_secrets_changelog'),
        ('ipam', '0050_iprange'),
    ]

    operations = [
        migrations.CreateModel(
            name='WirelessLANGroup',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='wireless.wirelesslangroup')),
            ],
            options={
                'ordering': ('name', 'pk'),
                'unique_together': {('parent', 'name')},
            },
        ),
        migrations.CreateModel(
            name='WirelessLAN',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ssid', models.CharField(max_length=32)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wireless_lans', to='wireless.wirelesslangroup')),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlan')),
            ],
            options={
                'verbose_name': 'Wireless LAN',
                'ordering': ('ssid', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='WirelessLink',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ssid', models.CharField(blank=True, max_length=32)),
                ('status', models.CharField(default='connected', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('_interface_a_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('_interface_b_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('interface_a', models.ForeignKey(limit_choices_to={'type__in': ['ieee802.11a', 'ieee802.11g', 'ieee802.11n', 'ieee802.11ac', 'ieee802.11ad', 'ieee802.11ax']}, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface')),
                ('interface_b', models.ForeignKey(limit_choices_to={'type__in': ['ieee802.11a', 'ieee802.11g', 'ieee802.11n', 'ieee802.11ac', 'ieee802.11ad', 'ieee802.11ax']}, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['pk'],
                'unique_together': {('interface_a', 'interface_b')},
            },
        ),
    ]
