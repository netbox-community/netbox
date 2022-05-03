from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0145_site_remove_deprecated_fields'),
        ('tenancy', '0004_extend_tag_support'),
    ]

    operations = [
        # Model IDs
        migrations.AlterField(
            model_name='contact',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contactassignment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contactgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='contactrole',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),

        # GFK IDs
        migrations.AlterField(
            model_name='contactassignment',
            name='object_id',
            field=models.PositiveBigIntegerField(),
        ),
    ]
