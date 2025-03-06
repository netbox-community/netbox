from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0099_cachedvalue_ordering'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('tenancy', '0012_contactassignment_custom_fields'),
        ('ipam', '0068_move_l2vpn'),
        ('vpn', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
                        ('description', models.CharField(blank=True, max_length=200)),
                        ('comments', models.TextField(blank=True)),
                        ('name', models.CharField(max_length=100, unique=True)),
                        ('slug', models.SlugField(max_length=100, unique=True)),
                        ('type', models.CharField(max_length=50)),
                        ('identifier', models.BigIntegerField(blank=True, null=True)),
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
                        'verbose_name_plural': 'L2VPNs',
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
                                on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='vpn.l2vpn'
                            ),
                        ),
                        ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                    ],
                    options={
                        'verbose_name': 'L2VPN termination',
                        'verbose_name_plural': 'L2VPN terminations',
                        'ordering': ('l2vpn',),
                    },
                ),
            ],
            # Tables have been renamed from ipam
            database_operations=[],
        ),
        migrations.AddConstraint(
            model_name='l2vpntermination',
            constraint=models.UniqueConstraint(
                fields=('assigned_object_type', 'assigned_object_id'), name='vpn_l2vpntermination_assigned_object'
            ),
        ),
        migrations.AddIndex(
            model_name='l2vpntermination',
            index=models.Index(
                fields=['assigned_object_type', 'assigned_object_id'], name='vpn_l2vpnte_assigne_9c55f8_idx'
            ),
        ),
    ]
