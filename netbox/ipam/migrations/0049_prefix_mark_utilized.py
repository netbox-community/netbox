from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0048_prefix_populate_depth_children'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='mark_utilized',
            field=models.BooleanField(default=False),
        ),
    ]
