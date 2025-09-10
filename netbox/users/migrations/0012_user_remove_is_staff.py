from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_concrete_objecttype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_staff',
        ),
    ]
