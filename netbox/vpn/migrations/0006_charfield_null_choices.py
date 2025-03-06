from django.db import migrations, models


def set_null_values(apps, schema_editor):
    """
    Replace empty strings with null values.
    """
    IKEPolicy = apps.get_model('vpn', 'IKEPolicy')
    IKEProposal = apps.get_model('vpn', 'IKEProposal')
    IPSecProposal = apps.get_model('vpn', 'IPSecProposal')

    IKEPolicy.objects.filter(mode='').update(mode=None)
    IKEProposal.objects.filter(authentication_algorithm='').update(authentication_algorithm=None)
    IPSecProposal.objects.filter(authentication_algorithm='').update(authentication_algorithm=None)
    IPSecProposal.objects.filter(encryption_algorithm='').update(encryption_algorithm=None)


class Migration(migrations.Migration):
    dependencies = [
        ('vpn', '0005_rename_indexes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ikepolicy',
            name='mode',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ikeproposal',
            name='authentication_algorithm',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipsecproposal',
            name='authentication_algorithm',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ipsecproposal',
            name='encryption_algorithm',
            field=models.CharField(blank=True, null=True),
        ),
        migrations.RunPython(code=set_null_values, reverse_code=migrations.RunPython.noop),
    ]
