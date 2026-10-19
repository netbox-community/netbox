from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0144_customfield_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taggeditem',
            name='object_id',
            field=models.PositiveBigIntegerField(db_index=True),
        ),
    ]
