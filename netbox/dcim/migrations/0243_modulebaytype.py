import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.fields
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0242_add_devicetype_end_of_life'),
        ('extras', '0141_custom_field_nulls_first'),
        ('users', '0016_default_ordering_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleBayType',
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
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('color', utilities.fields.ColorField(blank=True, max_length=6)),
                (
                    'manufacturer',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='module_bay_types',
                        to='dcim.manufacturer',
                    ),
                ),
                (
                    'owner',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='+',
                        to='users.owner',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'module bay type',
                'verbose_name_plural': 'module bay types',
                'ordering': ('manufacturer', 'name'),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name='modulebay',
            name='module_bay_types',
            field=models.ManyToManyField(blank=True, related_name='module_bays', to='dcim.modulebaytype'),
        ),
        migrations.AddField(
            model_name='modulebaytemplate',
            name='module_bay_types',
            field=models.ManyToManyField(blank=True, related_name='module_bay_templates', to='dcim.modulebaytype'),
        ),
        migrations.AddField(
            model_name='moduletype',
            name='module_bay_types',
            field=models.ManyToManyField(blank=True, related_name='module_types', to='dcim.modulebaytype'),
        ),
        migrations.AddConstraint(
            model_name='modulebaytype',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'name'),
                name='dcim_modulebaytype_unique_manufacturer_name',
                nulls_distinct=False,
            ),
        ),
        migrations.AddConstraint(
            model_name='modulebaytype',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='dcim_modulebaytype_unique_manufacturer_slug',
                nulls_distinct=False,
            ),
        ),
    ]
