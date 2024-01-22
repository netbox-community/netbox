from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0059_exporttemplate_as_attachment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlink',
            name='button_class',
            field=models.CharField(default='outline-dark', max_length=30),
        ),
    ]
