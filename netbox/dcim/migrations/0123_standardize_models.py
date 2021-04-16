import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0122_standardize_name_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='consoleport',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='devicerole',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='frontport',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='frontport',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='frontport',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='interface',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='interface',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='manufacturer',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='platform',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='powerport',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='powerport',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='powerport',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='rackgroup',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='rackrole',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='rearport',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rearport',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AddField(
            model_name='rearport',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='region',
            name='custom_field_data',
            field=models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
        ),
        migrations.AlterField(
            model_name='cable',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='cablepath',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='device',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicerole',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='devicetype',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='interface',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='manufacturer',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='platform',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerpanel',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rack',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rackgroup',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rackreservation',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rackrole',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='region',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='site',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
