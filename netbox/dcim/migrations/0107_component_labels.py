from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0106_role_default_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='consoleport',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='consoleporttemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='consoleserverport',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='consoleserverporttemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='devicebay',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='devicebaytemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='frontport',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='interface',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='interfacetemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='powerport',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='rearport',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='label',
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
