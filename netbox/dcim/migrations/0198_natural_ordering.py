from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='site',
            options={'ordering': ('name',)},
        ),
        migrations.AlterField(
            model_name='site',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterModelOptions(
            name='consoleport',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='consoleporttemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='consoleserverport',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='consoleserverporttemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='device',
            options={'ordering': ('name', 'pk')},
        ),
        migrations.AlterModelOptions(
            name='devicebay',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='devicebaytemplate',
            options={'ordering': ('device_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='frontport',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='frontporttemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='interfacetemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'ordering': ('device__id', 'parent__id', 'name')},
        ),
        migrations.AlterModelOptions(
            name='inventoryitemtemplate',
            options={'ordering': ('device_type__id', 'parent__id', 'name')},
        ),
        migrations.AlterModelOptions(
            name='modulebay',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='modulebaytemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='poweroutlet',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='poweroutlettemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='powerport',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='powerporttemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.AlterModelOptions(
            name='rack',
            options={'ordering': ('site', 'location', 'name', 'pk')},
        ),
        migrations.AlterModelOptions(
            name='rearport',
            options={'ordering': ('device', 'name')},
        ),
        migrations.AlterModelOptions(
            name='rearporttemplate',
            options={'ordering': ('device_type', 'module_type', 'name')},
        ),
        migrations.RemoveField(
            model_name='consoleport',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='consoleporttemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='consoleserverport',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='consoleserverporttemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='device',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='devicebay',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='devicebaytemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='frontport',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='frontporttemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='inventoryitem',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='inventoryitemtemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='modulebay',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='modulebaytemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='poweroutlet',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='poweroutlettemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='powerport',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='powerporttemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='rack',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='rearport',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='rearporttemplate',
            name='_name',
        ),
        migrations.RemoveField(
            model_name='site',
            name='_name',
        ),
        migrations.AlterField(
            model_name='consoleport',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='device',
            name='name',
            field=models.CharField(blank=True, db_collation='natural_sort', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='devicebay',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='devicebaytemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='frontport',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='frontporttemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='interface',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='interfacetemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='inventoryitemtemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='modulebay',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='modulebaytemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlet',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='powerport',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='rack',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='rearport',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='rearporttemplate',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='powerfeed',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='powerpanel',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='virtualchassis',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='virtualdevicecontext',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
    ]
