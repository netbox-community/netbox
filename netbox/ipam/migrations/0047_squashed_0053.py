import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import ipam.fields
import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('ipam', '0047_prefix_depth_children'),
        ('ipam', '0048_prefix_populate_depth_children'),
        ('ipam', '0049_prefix_mark_utilized'),
        ('ipam', '0050_iprange'),
        ('ipam', '0051_extend_tag_support'),
        ('ipam', '0052_fhrpgroup'),
        ('ipam', '0053_asn_model')
    ]

    dependencies = [
        ('ipam', '0046_set_vlangroup_scope_types'),
        ('tenancy', '0001_squashed_0012'),
        ('extras', '0002_squashed_0059'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='_children',
            field=models.PositiveBigIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='prefix',
            name='_depth',
            field=models.PositiveSmallIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='prefix',
            name='mark_utilized',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='IPRange',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('start_address', ipam.fields.IPAddressField()),
                ('end_address', ipam.fields.IPAddressField()),
                ('size', models.PositiveIntegerField(editable=False)),
                ('status', models.CharField(default='active', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('role', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ip_ranges', to='ipam.role')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_ranges', to='tenancy.tenant')),
                ('vrf', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_ranges', to='ipam.vrf')),
            ],
            options={
                'verbose_name': 'IP range',
                'verbose_name_plural': 'IP ranges',
                'ordering': (models.OrderBy(models.F('vrf'), nulls_first=True), 'start_address', 'pk'),
            },
        ),
        migrations.AddField(
            model_name='rir',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='role',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.CreateModel(
            name='FHRPGroup',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('group_id', models.PositiveSmallIntegerField()),
                ('protocol', models.CharField(max_length=50)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('auth_key', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'FHRP group',
                'ordering': ['protocol', 'group_id', 'pk'],
            },
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'ipam'), ('model', 'fhrpgroup')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.CreateModel(
            name='FHRPGroupAssignment',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('interface_id', models.PositiveIntegerField()),
                ('priority', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)])),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipam.fhrpgroup')),
                ('interface_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'FHRP group assignment',
                'ordering': ('-priority', 'pk'),
                'unique_together': {('interface_type', 'interface_id', 'group')},
            },
        ),
        migrations.CreateModel(
            name='ASN',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('asn', ipam.fields.ASNField(unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('rir', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='asns', to='ipam.rir')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='asns', to='tenancy.tenant')),
            ],
            options={
                'verbose_name': 'ASN',
                'verbose_name_plural': 'ASNs',
                'ordering': ['asn'],
            },
        ),
    ]
