from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0003_initial'),
        ('virtualization', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0001_initial'),
        ('extras', '0002_initial'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='virtual_machine',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='virtualization.virtualmachine'),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='routetarget',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='route_targets', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prefixes', to='ipam.role'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='vlan',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.vlan'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='prefixes', to='ipam.vrf'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.ipaddress'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='vrf',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ip_addresses', to='ipam.vrf'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='rir',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aggregates', to='ipam.rir'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='aggregates', to='tenancy.tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='vlangroup',
            unique_together={('scope_type', 'scope_id', 'name'), ('scope_type', 'scope_id', 'slug')},
        ),
        migrations.AlterUniqueTogether(
            name='vlan',
            unique_together={('group', 'vid'), ('group', 'name')},
        ),
    ]
