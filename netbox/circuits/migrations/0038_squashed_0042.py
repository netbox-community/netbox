import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):

    replaces = [
        ('circuits', '0038_cabling_cleanup'),
        ('circuits', '0039_unique_constraints'),
        ('circuits', '0040_provider_remove_deprecated_fields'),
        ('circuits', '0041_standardize_description_comments'),
        ('circuits', '0042_provideraccount')
    ]

    dependencies = [
        ('circuits', '0037_new_cabling_models'),
        ('dcim', '0160_populate_cable_ends'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='circuittermination',
            name='_link_peer_id',
        ),
        migrations.RemoveField(
            model_name='circuittermination',
            name='_link_peer_type',
        ),
        migrations.RemoveConstraint(
            model_name='providernetwork',
            name='circuits_providernetwork_provider_name',
        ),
        migrations.AlterUniqueTogether(
            name='circuit',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='circuittermination',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='providernetwork',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='circuit',
            constraint=models.UniqueConstraint(fields=('provider', 'cid'), name='circuits_circuit_unique_provider_cid'),
        ),
        migrations.AddConstraint(
            model_name='circuittermination',
            constraint=models.UniqueConstraint(fields=('circuit', 'term_side'), name='circuits_circuittermination_unique_circuit_term_side'),
        ),
        migrations.AddConstraint(
            model_name='providernetwork',
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_providernetwork_unique_provider_name'),
        ),
        migrations.RemoveField(
            model_name='provider',
            name='admin_contact',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='asn',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='noc_contact',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='portal_url',
        ),
        migrations.AddField(
            model_name='provider',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.CreateModel(
            name='ProviderAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('account', models.CharField(max_length=100)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accounts', to='circuits.provider')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('provider', 'account'),
            },
        ),
        migrations.AddConstraint(
            model_name='provideraccount',
            constraint=models.UniqueConstraint(condition=models.Q(('name', ''), _negated=True), fields=('provider', 'name'), name='circuits_provideraccount_unique_provider_name'),
        ),
        migrations.AddConstraint(
            model_name='provideraccount',
            constraint=models.UniqueConstraint(fields=('provider', 'account'), name='circuits_provideraccount_unique_provider_account'),
        ),
        migrations.RemoveField(
            model_name='provider',
            name='account',
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provideraccount'),
            preserve_default=False,
        ),
        migrations.AlterModelOptions(
            name='circuit',
            options={'ordering': ['provider', 'provider_account', 'cid']},
        ),
        migrations.AddConstraint(
            model_name='circuit',
            constraint=models.UniqueConstraint(fields=('provider_account', 'cid'), name='circuits_circuit_unique_provideraccount_cid'),
        ),
    ]
