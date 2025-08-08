from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0129_fix_script_paths'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageattachment',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
