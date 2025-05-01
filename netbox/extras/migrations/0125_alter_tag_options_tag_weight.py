from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0124_remove_staging'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'ordering': ('weight', 'name')},
        ),
        migrations.AddField(
            model_name='tag',
            name='weight',
            field=models.PositiveSmallIntegerField(default=1000),
        ),
    ]
