from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0144_fix_cable_abs_length'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='asn',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_email',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_name',
        ),
        migrations.RemoveField(
            model_name='site',
            name='contact_phone',
        ),
    ]
