from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0117_move_objectchange'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='unique',
            field=models.BooleanField(default=False),
        ),
    ]
