from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0058_journalentry'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttemplate',
            name='as_attachment',
            field=models.BooleanField(default=True),
        ),
    ]
