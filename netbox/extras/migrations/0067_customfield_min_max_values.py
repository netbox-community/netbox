from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0066_customfield_name_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='validation_maximum',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='validation_minimum',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
