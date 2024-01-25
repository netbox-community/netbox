import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('circuits', '0003_extend_tag_support'),
        ('circuits', '0004_rename_cable_peer'),
        ('circuits', '0032_provider_service_id'),
        ('circuits', '0033_standardize_id_fields'),
        ('circuits', '0034_created_datetimefield'),
        ('circuits', '0035_provider_asns'),
        ('circuits', '0036_circuit_termination_date_tags_custom_fields'),
        ('circuits', '0037_new_cabling_models')
    ]

    dependencies = [
        ('ipam', '0047_squashed_0053'),
        ('extras', '0002_squashed_0059'),
        ('circuits', '0002_squashed_0029'),
    ]

    operations = [
        migrations.AddField(
            model_name='circuittype',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.RenameField(
            model_name='circuittermination',
            old_name='_cable_peer_id',
            new_name='_link_peer_id',
        ),
        migrations.RenameField(
            model_name='circuittermination',
            old_name='_cable_peer_type',
            new_name='_link_peer_type',
        ),
        migrations.AddField(
            model_name='providernetwork',
            name='service_id',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='provider',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='providernetwork',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='circuit',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='provider',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='providernetwork',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='provider',
            name='asns',
            field=models.ManyToManyField(blank=True, related_name='providers', to='ipam.asn'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='termination_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable_end',
            field=models.CharField(blank=True, max_length=1),
        ),
    ]
