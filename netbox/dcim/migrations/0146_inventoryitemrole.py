import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.fields


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0067_configcontext_cluster_types'),
        ('dcim', '0145_modules'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItemRole',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('color', utilities.fields.ColorField(default='9e9e9e', max_length=6)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='inventory_items', to='dcim.inventoryitemrole'),
        ),
    ]
