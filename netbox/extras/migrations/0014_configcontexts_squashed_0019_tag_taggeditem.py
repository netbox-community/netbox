import django.contrib.postgres.fields.jsonb
import django.db.models.deletion
from django.db import migrations, models


def set_template_language(apps, schema_editor):
    """
    Set the language for all existing ExportTemplates to Django (Jinja2 is the default for new ExportTemplates).
    """
    ExportTemplate = apps.get_model('extras', 'ExportTemplate')
    ExportTemplate.objects.update(template_language=10)


class Migration(migrations.Migration):

    replaces = [('extras', '0014_configcontexts'), ('extras', '0015_remove_useraction'), ('extras', '0016_exporttemplate_add_cable'), ('extras', '0017_exporttemplate_mime_type_length'), ('extras', '0018_exporttemplate_add_jinja2'), ('extras', '0019_tag_taggeditem')]

    dependencies = [
        ('extras', '0013_objectchange'),
        ('tenancy', '0005_change_logging'),
        ('dcim', '0061_platform_napalm_args'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('description', models.CharField(blank=True, max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('platforms', models.ManyToManyField(blank=True, related_name='_configcontext_platforms_+', to='dcim.Platform')),
                ('regions', models.ManyToManyField(blank=True, related_name='_configcontext_regions_+', to='dcim.Region')),
                ('roles', models.ManyToManyField(blank=True, related_name='_configcontext_roles_+', to='dcim.DeviceRole')),
                ('sites', models.ManyToManyField(blank=True, related_name='_configcontext_sites_+', to='dcim.Site')),
                ('tenant_groups', models.ManyToManyField(blank=True, related_name='_configcontext_tenant_groups_+', to='tenancy.TenantGroup')),
                ('tenants', models.ManyToManyField(blank=True, related_name='_configcontext_tenants_+', to='tenancy.Tenant')),
            ],
            options={
                'ordering': ['weight', 'name'],
            },
        ),
        migrations.AlterField(
            model_name='customfield',
            name='obj_type',
            field=models.ManyToManyField(help_text='The object(s) to which this field applies.', limit_choices_to={'model__in': ('provider', 'circuit', 'site', 'rack', 'devicetype', 'device', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service', 'secret', 'tenant', 'cluster', 'virtualmachine')}, related_name='custom_fields', to='contenttypes.ContentType', verbose_name='Object(s)'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ['provider', 'circuit', 'site', 'region', 'rack', 'rackgroup', 'manufacturer', 'devicetype', 'device', 'consoleport', 'powerport', 'interfaceconnection', 'virtualchassis', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service', 'secret', 'tenant', 'cluster', 'virtualmachine']}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='obj_type',
            field=models.ManyToManyField(help_text='The object(s) to which this Webhook applies.', limit_choices_to={'model__in': ('provider', 'circuit', 'site', 'rack', 'devicetype', 'device', 'virtualchassis', 'consoleport', 'consoleserverport', 'powerport', 'poweroutlet', 'interface', 'devicebay', 'inventoryitem', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service', 'secret', 'tenant', 'cluster', 'virtualmachine')}, related_name='webhooks', to='contenttypes.ContentType', verbose_name='Object types'),
        ),
        migrations.DeleteModel(
            name='UserAction',
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(limit_choices_to={'model__in': ['provider', 'circuit', 'site', 'region', 'rack', 'rackgroup', 'manufacturer', 'devicetype', 'device', 'consoleport', 'powerport', 'interface', 'cable', 'virtualchassis', 'aggregate', 'prefix', 'ipaddress', 'vlan', 'vrf', 'service', 'secret', 'tenant', 'cluster', 'virtualmachine']}, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='mime_type',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='template_language',
            field=models.PositiveSmallIntegerField(default=20),
        ),
        migrations.RunPython(
            code=set_template_language,
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TaggedItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.IntegerField(db_index=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras_taggeditem_tagged_items', to='contenttypes.ContentType')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='extras_taggeditem_items', to='extras.Tag')),
            ],
            options={
                'abstract': False,
                'index_together': {('content_type', 'object_id')},
            },
        ),
    ]
