import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import netbox.models.deletion
import utilities.json


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0227_rack_group'),
        ('extras', '0134_owner'),
        ('users', '0015_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='CableBundle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(
                    blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)
                 ),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('owner', models.ForeignKey(
                    blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='users.owner')
                 ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'cable bundle',
                'verbose_name_plural': 'cable bundles',
                'ordering': ('name',),
            },
            bases=(netbox.models.deletion.DeleteMixin, models.Model),
        ),
        migrations.AddField(
            model_name='cable',
            name='bundle',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='cables',
                to='dcim.cablebundle',
                verbose_name='bundle',
            ),
        ),
    ]
