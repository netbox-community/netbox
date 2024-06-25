from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0116_move_objectchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='validation_unique',
            field=models.BooleanField(default=False),
        ),
    ]
