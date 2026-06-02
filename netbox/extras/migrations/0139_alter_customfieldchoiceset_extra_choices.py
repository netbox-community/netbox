from django.db import migrations

import extras.fields


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0138_customfieldchoiceset_choice_colors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldchoiceset',
            name='extra_choices',
            field=extras.fields.ChoiceSetField(blank=True, null=True),
        ),
    ]
