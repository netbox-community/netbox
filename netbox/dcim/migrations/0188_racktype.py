import django.core.validators
import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import utilities.fields
import utilities.json
import utilities.ordering


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0118_customfield_uniqueness'),
        ('dcim', '0187_alter_device_vc_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='RackType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(
                    blank=True,
                    default=dict,
                    encoder=utilities.json.CustomFieldJSONEncoder
                )),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('weight', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('weight_unit', models.CharField(blank=True, max_length=50)),
                ('_abs_weight', models.PositiveBigIntegerField(blank=True, null=True)),
                ('manufacturer', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='rack_types',
                    to='dcim.manufacturer'
                )),
                ('model', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('form_factor', models.CharField(blank=True, max_length=50)),
                ('width', models.PositiveSmallIntegerField(default=19)),
                ('u_height', models.PositiveSmallIntegerField(
                    default=42,
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(100),
                    ]
                )),
                ('starting_unit', models.PositiveSmallIntegerField(
                    default=1,
                    validators=[django.core.validators.MinValueValidator(1)]
                )),
                ('desc_units', models.BooleanField(default=False)),
                ('outer_width', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('outer_depth', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('outer_unit', models.CharField(blank=True, max_length=50)),
                ('max_weight', models.PositiveIntegerField(blank=True, null=True)),
                ('_abs_max_weight', models.PositiveBigIntegerField(blank=True, null=True)),
                ('mounting_depth', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'racktype',
                'verbose_name_plural': 'racktypes',
                'ordering': ('manufacturer', 'model'),
            },
        ),
        migrations.RenameField(
            model_name='rack',
            old_name='type',
            new_name='form_factor',
        ),
        migrations.AddField(
            model_name='rack',
            name='rack_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='racks',
                to='dcim.racktype',
            ),
        ),
        migrations.AddConstraint(
            model_name='racktype',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'model'), name='dcim_racktype_unique_manufacturer_model'
            ),
        ),
        migrations.AddConstraint(
            model_name='racktype',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'slug'), name='dcim_racktype_unique_manufacturer_slug'
            ),
        ),
    ]
