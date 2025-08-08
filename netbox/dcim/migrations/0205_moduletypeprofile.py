import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import utilities.json
import utilities.jsonschema


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0204_device_role_rebuild'),
        ('extras', '0126_exporttemplate_file_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleTypeProfile',
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
                ('schema', models.JSONField(blank=True, null=True, validators=[utilities.jsonschema.validate_schema])),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'module type profile',
                'verbose_name_plural': 'module type profiles',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='moduletype',
            name='attribute_data',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='profile',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='module_types',
                to='dcim.moduletypeprofile',
            ),
        ),
        migrations.AlterModelOptions(
            name='moduletype',
            options={'ordering': ('profile', 'manufacturer', 'model')},
        ),
    ]
