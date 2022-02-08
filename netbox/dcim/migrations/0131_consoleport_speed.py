from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0130_sitegroup'),
    ]

    operations = [
        migrations.AlterField(
            model_name='consoleport',
            name='speed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consoleserverport',
            name='speed',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
