from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dcim", "0237_module_remove_local_context_data"),
    ]

    operations = [
        migrations.AddField(
            model_name="portmapping",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="portmapping",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name="porttemplatemapping",
            name="created",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name="porttemplatemapping",
            name="last_updated",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
