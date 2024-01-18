from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers
import utilities.json
import wireless.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('ipam', '0001_initial'),
        ('dcim', '0002_squashed'),
        ('tenancy', '0001_initial'),
    ]

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

    operations = [
        migrations.CreateModel(
            name='WirelessLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('auth_cipher', models.CharField(blank=True, max_length=50)),
                ('auth_psk', models.CharField(blank=True, max_length=64)),
                ('ssid', models.CharField(blank=True, max_length=32)),
                ('status', models.CharField(default='connected', max_length=50)),
                ('_interface_a_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('_interface_b_device', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='dcim.device')),
                ('interface_a', models.ForeignKey(limit_choices_to=wireless.models.get_wireless_interface_types, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface')),
                ('interface_b', models.ForeignKey(limit_choices_to=wireless.models.get_wireless_interface_types, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='dcim.interface')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='wireless_links', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'wireless link',
                'verbose_name_plural': 'wireless links',
                'ordering': ['pk'],
            },
        ),
        migrations.CreateModel(
            name='WirelessLANGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='wireless.wirelesslangroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'wireless LAN group',
                'verbose_name_plural': 'wireless LAN groups',
                'ordering': ('name', 'pk'),
            },
        ),
        migrations.CreateModel(
            name='WirelessLAN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('auth_cipher', models.CharField(blank=True, max_length=50)),
                ('auth_psk', models.CharField(blank=True, max_length=64)),
                ('ssid', models.CharField(max_length=32)),
                ('status', models.CharField(default='active', max_length=50)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wireless_lans', to='wireless.wirelesslangroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='wireless_lans', to='tenancy.tenant')),
                ('vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlan')),
            ],
            options={
                'verbose_name': 'wireless LAN',
                'verbose_name_plural': 'wireless LANs',
                'ordering': ('ssid', 'pk'),
            },
        ),
        migrations.AddConstraint(
            model_name='wirelesslink',
            constraint=models.UniqueConstraint(fields=('interface_a', 'interface_b'), name='wireless_wirelesslink_unique_interfaces'),
        ),
        migrations.AddConstraint(
            model_name='wirelesslangroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='wireless_wirelesslangroup_unique_parent_name'),
        ),
    ]
