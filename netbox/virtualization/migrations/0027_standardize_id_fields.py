from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0145_site_remove_deprecated_fields'),
        ('virtualization', '0026_vminterface_bridge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cluster',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='clustergroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='clustertype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='vminterface',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
