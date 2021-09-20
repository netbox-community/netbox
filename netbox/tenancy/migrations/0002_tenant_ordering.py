from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0001_squashed_0012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tenant',
            options={'ordering': ['name']},
        ),
    ]
