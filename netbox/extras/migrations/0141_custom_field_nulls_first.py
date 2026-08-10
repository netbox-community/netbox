from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0140_imageattachment_image_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="customfield",
            name="nulls_first",
            field=models.BooleanField(default=True),
        ),
    ]
