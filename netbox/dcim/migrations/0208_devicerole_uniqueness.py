from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0207_remove_redundant_indexes'),
        ('extras', '0129_fix_script_paths'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'),
                name='dcim_devicerole_parent_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent__isnull', True)),
                fields=('name',),
                name='dcim_devicerole_name',
                violation_error_message='A top-level device role with this name already exists.'
            ),
        ),
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                fields=('parent', 'slug'),
                name='dcim_devicerole_parent_slug'
            ),
        ),
        migrations.AddConstraint(
            model_name='devicerole',
            constraint=models.UniqueConstraint(
                condition=models.Q(('parent__isnull', True)),
                fields=('slug',),
                name='dcim_devicerole_slug',
                violation_error_message='A top-level device role with this slug already exists.'
            ),
        ),
    ]
