from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0137_default_ordering_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfieldchoiceset',
            name='choice_colors',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
