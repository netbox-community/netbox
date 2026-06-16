from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("extras", "0139_alter_customfieldchoiceset_extra_choices"),
    ]

    operations = [
        migrations.AddField(
            model_name="customfield",
            name="nulls_first",
            field=models.BooleanField(default=True),
        ),
    ]
