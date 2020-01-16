import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('ipam', '0021_vrf_ordering'), ('ipam', '0022_tags'), ('ipam', '0023_change_logging'), ('ipam', '0024_vrf_allow_null_rd'), ('ipam', '0025_custom_tag_models')]

    dependencies = [
        ('ipam', '0020_ipaddress_add_role_carp'),
        ('taggit', '0002_auto_20150616_2121'),
        ('extras', '0019_tag_taggeditem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vrf',
            options={'ordering': ['name', 'rd'], 'verbose_name': 'VRF', 'verbose_name_plural': 'VRFs'},
        ),
        migrations.AddField(
            model_name='rir',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rir',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='aggregate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='prefix',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='vlan',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='rd',
            field=models.CharField(blank=True, max_length=21, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='aggregate',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='ipaddress',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='prefix',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='service',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='vlan',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='vrf',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
    ]
