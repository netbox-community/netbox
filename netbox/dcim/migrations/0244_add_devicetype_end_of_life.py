from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0243_consolidate_unique_constraints"),
    ]

    operations = [
        migrations.AddField(
            model_name="devicetype",
            name="end_of_life",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="moduletype",
            name="end_of_life",
            field=models.DateField(blank=True, null=True),
        ),
    ]
