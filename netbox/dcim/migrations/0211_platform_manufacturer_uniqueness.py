from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0210_macaddress_ordering'),
        ('extras', '0129_fix_script_paths'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='platform',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'name'),
                name='dcim_platform_manufacturer_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                condition=models.Q(('manufacturer__isnull', True)),
                fields=('name',),
                name='dcim_platform_name',
                violation_error_message='Platform name must be unique.'
            ),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='dcim_platform_manufacturer_slug'
            ),
        ),
        migrations.AddConstraint(
            model_name='platform',
            constraint=models.UniqueConstraint(
                condition=models.Q(('manufacturer__isnull', True)),
                fields=('slug',),
                name='dcim_platform_slug',
                violation_error_message='Platform slug must be unique.'
            ),
        ),
    ]
