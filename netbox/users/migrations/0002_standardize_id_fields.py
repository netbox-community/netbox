from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_squashed_0011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectpermission',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='token',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userconfig',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]
