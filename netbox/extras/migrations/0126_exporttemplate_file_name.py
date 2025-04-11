from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0125_alter_tag_options_tag_weight'),
    ]

    operations = [
        migrations.AddField(
            model_name='exporttemplate',
            name='file_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
