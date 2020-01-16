import taggit.managers
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('dcim', '0067_device_type_remove_qualifiers'), ('dcim', '0068_rack_new_fields'), ('dcim', '0069_deprecate_nullablecharfield'), ('dcim', '0070_custom_tag_models')]

    dependencies = [
        ('extras', '0019_tag_taggeditem'),
        ('dcim', '0066_cables'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='devicetype',
            name='is_console_server',
        ),
        migrations.RemoveField(
            model_name='devicetype',
            name='is_network_device',
        ),
        migrations.RemoveField(
            model_name='devicetype',
            name='is_pdu',
        ),
        migrations.RemoveField(
            model_name='devicetype',
            name='interface_ordering',
        ),
        migrations.AddField(
            model_name='rack',
            name='status',
            field=models.PositiveSmallIntegerField(default=3),
        ),
        migrations.AddField(
            model_name='rack',
            name='outer_depth',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='outer_unit',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='outer_width',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='asset_tag',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='asset_tag',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='rack',
            name='asset_tag',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='rack',
            name='facility_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='device',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='interface',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='rack',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='site',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags'),
        ),
    ]
