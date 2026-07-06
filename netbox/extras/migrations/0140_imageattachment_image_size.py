from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0139_alter_customfieldchoiceset_extra_choices"),
    ]

    operations = [
        migrations.AddField(
            model_name="imageattachment",
            name="image_size",
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
