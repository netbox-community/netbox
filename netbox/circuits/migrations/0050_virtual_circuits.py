import django.db.models.deletion
import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):
    dependencies = [
        ('circuits', '0049_natural_ordering'),
        ('dcim', '0196_qinq_svlan'),
        ('extras', '0122_charfield_null_choices'),
        ('tenancy', '0016_charfield_null_choices'),
    ]

    operations = [
        migrations.CreateModel(
            name='VirtualCircuit',
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
                ('cid', models.CharField(max_length=100)),
                ('status', models.CharField(default='active', max_length=50)),
                (
                    'provider_account',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='virtual_circuits',
                        to='circuits.provideraccount',
                    ),
                ),
                (
                    'provider_network',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='virtual_circuits',
                        to='circuits.providernetwork',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'tenant',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='virtual_circuits',
                        to='tenancy.tenant',
                    ),
                ),
            ],
            options={
                'verbose_name': 'circuit',
                'verbose_name_plural': 'circuits',
                'ordering': ['provider_network', 'provider_account', 'cid'],
            },
        ),
        migrations.CreateModel(
            name='VirtualCircuitTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('role', models.CharField(default='peer', max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'interface',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='virtual_circuit_termination',
                        to='dcim.interface',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                (
                    'virtual_circuit',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='terminations',
                        to='circuits.virtualcircuit',
                    ),
                ),
            ],
            options={
                'verbose_name': 'virtual circuit termination',
                'verbose_name_plural': 'virtual circuit terminations',
                'ordering': ['virtual_circuit', 'role', 'pk'],
            },
        ),
        migrations.AddConstraint(
            model_name='virtualcircuit',
            constraint=models.UniqueConstraint(
                fields=('provider_network', 'cid'), name='circuits_virtualcircuit_unique_provider_network_cid'
            ),
        ),
        migrations.AddConstraint(
            model_name='virtualcircuit',
            constraint=models.UniqueConstraint(
                fields=('provider_account', 'cid'), name='circuits_virtualcircuit_unique_provideraccount_cid'
            ),
        ),
    ]
