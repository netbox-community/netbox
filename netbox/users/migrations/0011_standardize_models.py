from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_update_jsonfield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectpermission',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='token',
            name='id',
            field=models.BigAutoField(primary_key=True, serialize=False),
        ),
    ]
