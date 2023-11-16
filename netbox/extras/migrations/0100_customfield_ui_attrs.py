from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0099_cachedvalue_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='ui_editable',
            field=models.CharField(default='yes', max_length=50),
        ),
        migrations.AddField(
            model_name='customfield',
            name='ui_visible',
            field=models.CharField(default='always', max_length=50),
        ),
    ]
