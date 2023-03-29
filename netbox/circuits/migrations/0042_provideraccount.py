from django.db import migrations, models
import django.db.models.deletion
import taggit.managers
import utilities.json


def create_provideraccounts_from_providers(apps, schema_editor):
    """
    Migrate Account in Provider model to separate account model
    """
    Provider = apps.get_model('circuits', 'Provider')
    ProviderAccount = apps.get_model('circuits', 'ProviderAccount')

    provider_accounts = []
    for provider in Provider.objects.all():
        if provider.account:
            provider_accounts.append(ProviderAccount(
                provider=provider,
                account=provider.account
            ))
    ProviderAccount.objects.bulk_create(provider_accounts, batch_size=100)


def restore_providers_from_provideraccounts(apps, schema_editor):
    """
    Restore Provider account values from auto-generated ProviderAccounts
    """
    ProviderAccount = apps.get_model('circuits', 'ProviderAccount')
    provider_accounts = ProviderAccount.objects.order_by('pk')
    for provideraccount in provider_accounts:
        if provider_accounts.filter(provider=provideraccount.provider)[0] == provideraccount:
            provideraccount.provider.account = provideraccount.account
            provideraccount.provider.save()


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0084_staging'),
        ('circuits', '0041_standardize_description_comments'),
    ]

    operations = [
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
        migrations.RunPython(
            create_provideraccounts_from_providers, restore_providers_from_provideraccounts
        ),
        migrations.RemoveField(
            model_name='provider',
            name='account',
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provideraccount', null=True, blank=True),
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
