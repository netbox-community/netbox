import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0043_circuittype_color'),
        ('extras', '0119_notifications'),
        ('tenancy', '0015_contactassignment_rename_content_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='CircuitGroup',
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
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='circuit_groups',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Circuit group',
                'verbose_name_plural': 'Circuit group',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='CircuitGroupAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('priority', models.CharField(blank=True, max_length=50)),
                (
                    'circuit',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='assignments',
                        to='circuits.circuit',
                    ),
                ),
                (
                    'group',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='assignments',
                        to='circuits.circuitgroup',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Circuit group assignment',
                'verbose_name_plural': 'Circuit group assignments',
                'ordering': ('group', 'circuit', 'priority', 'pk'),
            },
        ),
        migrations.AddConstraint(
            model_name='circuitgroupassignment',
            constraint=models.UniqueConstraint(
                fields=('circuit', 'group'), name='circuits_circuitgroupassignment_unique_circuit_group'
            ),
        ),
    ]
