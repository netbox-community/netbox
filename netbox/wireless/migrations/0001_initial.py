import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ipam', '0050_iprange'),
        ('extras', '0062_clear_secrets_changelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='WirelessLAN',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('ssid', models.CharField(max_length=32)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('vlan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ipam.vlan')),
            ],
            options={
                'verbose_name': 'Wireless LAN',
                'ordering': ('ssid', 'pk'),
            },
        ),
    ]
