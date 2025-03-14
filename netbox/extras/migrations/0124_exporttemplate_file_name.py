from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0123_remove_staging'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttemplate',
            name='file_name',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
