from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0099_cachedvalue_ordering'),
        ('ipam', '0067_ipaddress_index_host'),
        ('tenancy', '0012_contactassignment_custom_fields'),
    ]

    operations = [
        # IKE
        migrations.CreateModel(
            name='IKEProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('authentication_method', models.CharField()),
                ('encryption_algorithm', models.CharField()),
                ('authentication_algorithm', models.CharField(blank=True)),
                ('group', models.PositiveSmallIntegerField()),
                ('sa_lifetime', models.PositiveIntegerField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'IKE proposal',
                'verbose_name_plural': 'IKE proposals',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IKEPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('version', models.PositiveSmallIntegerField(default=2)),
                ('mode', models.CharField()),
                ('preshared_key', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'IKE policy',
                'verbose_name_plural': 'IKE policies',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='ikepolicy',
            name='proposals',
            field=models.ManyToManyField(related_name='ike_policies', to='vpn.ikeproposal'),
        ),
        migrations.AddField(
            model_name='ikepolicy',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        # IPSec
        migrations.CreateModel(
            name='IPSecProposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('encryption_algorithm', models.CharField(blank=True)),
                ('authentication_algorithm', models.CharField(blank=True)),
                ('sa_lifetime_seconds', models.PositiveIntegerField(blank=True, null=True)),
                ('sa_lifetime_data', models.PositiveIntegerField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'IPSec proposal',
                'verbose_name_plural': 'IPSec proposals',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='IPSecPolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('pfs_group', models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'IPSec policy',
                'verbose_name_plural': 'IPSec policies',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='ipsecpolicy',
            name='proposals',
            field=models.ManyToManyField(related_name='ipsec_policies', to='vpn.ipsecproposal'),
        ),
        migrations.AddField(
            model_name='ipsecpolicy',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.CreateModel(
            name='IPSecProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('mode', models.CharField()),
                (
                    'ike_policy',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='ipsec_profiles', to='vpn.ikepolicy'
                    ),
                ),
                (
                    'ipsec_policy',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='ipsec_profiles', to='vpn.ipsecpolicy'
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'IPSec profile',
                'verbose_name_plural': 'IPSec profiles',
                'ordering': ('name',),
            },
        ),
        # Tunnels
        migrations.CreateModel(
            name='TunnelGroup',
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
                ('description', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'tunnel group',
                'verbose_name_plural': 'tunnel groups',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='tunnelgroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.CreateModel(
            name='Tunnel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('status', models.CharField(default='active', max_length=50)),
                (
                    'group',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='tunnels',
                        to='vpn.tunnelgroup',
                    ),
                ),
                ('encapsulation', models.CharField(max_length=50)),
                ('tunnel_id', models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    'ipsec_profile',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='tunnels',
                        to='vpn.ipsecprofile',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='tunnels',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'tunnel',
                'verbose_name_plural': 'tunnels',
                'ordering': ('name',),
            },
        ),
        migrations.AddConstraint(
            model_name='tunnel',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='vpn_tunnel_group_name'),
        ),
        migrations.AddConstraint(
            model_name='tunnel',
            constraint=models.UniqueConstraint(
                condition=models.Q(('group__isnull', True)), fields=('name',), name='vpn_tunnel_name'
            ),
        ),
        migrations.CreateModel(
            name='TunnelTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('role', models.CharField(default='peer', max_length=50)),
                ('termination_id', models.PositiveBigIntegerField(blank=True, null=True)),
                (
                    'termination_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'
                    ),
                ),
                (
                    'outside_ip',
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='tunnel_termination',
                        to='ipam.ipaddress',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tunnel',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='vpn.tunnel'
                    ),
                ),
            ],
            options={
                'verbose_name': 'tunnel termination',
                'verbose_name_plural': 'tunnel terminations',
                'ordering': ('tunnel', 'role', 'pk'),
            },
        ),
        migrations.AddIndex(
            model_name='tunneltermination',
            index=models.Index(fields=['termination_type', 'termination_id'], name='vpn_tunnelt_termina_c1f04b_idx'),
        ),
        migrations.AddConstraint(
            model_name='tunneltermination',
            constraint=models.UniqueConstraint(
                fields=('termination_type', 'termination_id'),
                name='vpn_tunneltermination_termination',
                violation_error_message='An object may be terminated to only one tunnel at a time.',
            ),
        ),
    ]
