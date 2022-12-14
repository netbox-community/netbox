import django.contrib.postgres.fields
from utilities.json import CustomFieldJSONEncoder
import django.core.validators
from django.db import migrations, models
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0070_customlink_enabled'),
        ('ipam', '0054_vlangroup_min_max_vids'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServiceTemplate',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=CustomFieldJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('protocol', models.CharField(max_length=50)),
                ('ports', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(65535)]), size=None)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
    ]
