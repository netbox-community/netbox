import django.contrib.postgres.fields
import django.core.validators
import django.db.models.functions.comparison
import taggit.managers
from django.db import migrations, models

import ipam.fields
import ipam.lookups
import utilities.json


class Migration(migrations.Migration):
    replaces = [
        ('ipam', '0054_vlangroup_min_max_vids'),
        ('ipam', '0055_servicetemplate'),
        ('ipam', '0056_standardize_id_fields'),
        ('ipam', '0057_created_datetimefield'),
        ('ipam', '0058_ipaddress_nat_inside_nonunique'),
        ('ipam', '0059_l2vpn'),
        ('ipam', '0060_alter_l2vpn_slug'),
        ('ipam', '0061_fhrpgroup_name'),
        ('ipam', '0062_unique_constraints'),
        ('ipam', '0063_standardize_description_comments'),
        ('ipam', '0064_clear_search_cache'),
        ('ipam', '0065_asnrange'),
        ('ipam', '0066_iprange_mark_utilized'),
        ('ipam', '0067_ipaddress_index_host'),
    ]

    dependencies = [
        ('tenancy', '0007_contact_link'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0060_squashed_0086'),
        ('ipam', '0053_asn_model'),
        ('tenancy', '0009_standardize_description_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlangroup',
            name='max_vid',
            field=models.PositiveSmallIntegerField(
                default=4094,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4094),
                ],
            ),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='min_vid',
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(4094),
                ],
            ),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='asn',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='fhrpgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='fhrpgroupassignment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='iprange',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rir',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='role',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='routetarget',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='service',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='fhrpgroupassignment',
            name='interface_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='assigned_object_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='asn',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='fhrpgroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='fhrpgroupassignment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='iprange',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='rir',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='routetarget',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='ServiceTemplate',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('protocol', models.CharField(max_length=50)),
                (
                    'ports',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.PositiveIntegerField(
                            validators=[
                                django.core.validators.MinValueValidator(1),
                                django.core.validators.MaxValueValidator(65535),
                            ]
                        ),
                        size=None,
                    ),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AlterField(
            model_name='vlan',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='nat_outside',
                to='ipam.ipaddress',
            ),
        ),
        migrations.CreateModel(
            name='L2VPN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('type', models.CharField(max_length=50)),
                ('identifier', models.BigIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'export_targets',
                    models.ManyToManyField(blank=True, related_name='exporting_l2vpns', to='ipam.routetarget'),
                ),
                (
                    'import_targets',
                    models.ManyToManyField(blank=True, related_name='importing_l2vpns', to='ipam.routetarget'),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='l2vpns',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'L2VPN',
                'ordering': ('name', 'identifier'),
            },
        ),
        migrations.CreateModel(
            name='L2VPNTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('assigned_object_id', models.PositiveBigIntegerField()),
                (
                    'assigned_object_type',
                    models.ForeignKey(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(('app_label', 'dcim'), ('model', 'interface')),
                                models.Q(('app_label', 'ipam'), ('model', 'vlan')),
                                models.Q(('app_label', 'virtualization'), ('model', 'vminterface')),
                                _connector='OR',
                            )
                        ),
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='contenttypes.contenttype',
                    ),
                ),
                (
                    'l2vpn',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='ipam.l2vpn'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'L2VPN termination',
                'ordering': ('l2vpn',),
            },
        ),
        migrations.AddConstraint(
            model_name='l2vpntermination',
            constraint=models.UniqueConstraint(
                fields=('assigned_object_type', 'assigned_object_id'), name='ipam_l2vpntermination_assigned_object'
            ),
        ),
        migrations.AddField(
            model_name='fhrpgroup',
            name='name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='fhrpgroupassignment',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='vlangroup',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='fhrpgroupassignment',
            constraint=models.UniqueConstraint(
                fields=('interface_type', 'interface_id', 'group'),
                name='ipam_fhrpgroupassignment_unique_interface_group',
            ),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'vid'), name='ipam_vlan_unique_group_vid'),
        ),
        migrations.AddConstraint(
            model_name='vlan',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='ipam_vlan_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(
                fields=('scope_type', 'scope_id', 'name'), name='ipam_vlangroup_unique_scope_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='vlangroup',
            constraint=models.UniqueConstraint(
                fields=('scope_type', 'scope_id', 'slug'), name='ipam_vlangroup_unique_scope_slug'
            ),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='asn',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='fhrpgroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='iprange',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='l2vpn',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='prefix',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='service',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='servicetemplate',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vlan',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='vrf',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.CreateModel(
            name='ASNRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('start', ipam.fields.ASNField()),
                ('end', ipam.fields.ASNField()),
                (
                    'rir',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='asn_ranges', to='ipam.rir'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='asn_ranges',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'ASN range',
                'verbose_name_plural': 'ASN ranges',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='iprange',
            name='mark_utilized',
            field=models.BooleanField(default=False),
        ),
        migrations.AddIndex(
            model_name='ipaddress',
            index=models.Index(
                django.db.models.functions.comparison.Cast(
                    ipam.lookups.Host('address'), output_field=ipam.fields.IPAddressField()
                ),
                name='ipam_ipaddress_host',
            ),
        ),
    ]
