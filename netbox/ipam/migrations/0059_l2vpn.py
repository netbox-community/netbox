from utilities.json import CustomFieldJSONEncoder
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0075_configcontext_locations'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('tenancy', '0007_contact_link'),
        ('ipam', '0058_ipaddress_nat_inside_nonunique'),
    ]

    operations = [
        migrations.CreateModel(
            name='L2VPN',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField()),
                ('type', models.CharField(max_length=50)),
                ('identifier', models.BigIntegerField(blank=True, null=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('export_targets', models.ManyToManyField(blank=True, related_name='exporting_l2vpns', to='ipam.routetarget')),
                ('import_targets', models.ManyToManyField(blank=True, related_name='importing_l2vpns', to='ipam.routetarget')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('tenant', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='l2vpns', to='tenancy.tenant')),
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
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('assigned_object_id', models.PositiveBigIntegerField()),
                ('assigned_object_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'ipam'), ('model', 'vlan')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
                ('l2vpn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='ipam.l2vpn')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'L2VPN termination',
                'ordering': ('l2vpn',),
            },
        ),
        migrations.AddConstraint(
            model_name='l2vpntermination',
            constraint=models.UniqueConstraint(fields=('assigned_object_type', 'assigned_object_id'), name='ipam_l2vpntermination_assigned_object'),
        ),
    ]
