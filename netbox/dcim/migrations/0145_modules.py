import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.fields
import utilities.ordering


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0066_customfield_name_validation'),
        ('dcim', '0144_site_remove_deprecated_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModuleBayTemplate',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('label', models.CharField(blank=True, max_length=64)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('device_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modulebaytemplates', to='dcim.devicetype')),
            ],
            options={
                'ordering': ('device_type', '_name'),
                'unique_together': {('device_type', 'name')},
            },
        ),
        migrations.CreateModel(
            name='ModuleBay',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('_name', utilities.fields.NaturalOrderingField('name', blank=True, max_length=100, naturalize_function=utilities.ordering.naturalize)),
                ('label', models.CharField(blank=True, max_length=64)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modulebays', to='dcim.device')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('device', '_name'),
                'unique_together': {('device', 'name')},
            },
        ),
    ]
