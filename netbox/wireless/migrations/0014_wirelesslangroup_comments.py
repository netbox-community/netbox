from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0013_natural_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='wirelesslangroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
