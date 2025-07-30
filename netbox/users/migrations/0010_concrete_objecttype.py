from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('users', '0009_update_group_perms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectpermission',
            name='object_types',
            field=models.ManyToManyField(related_name='object_permissions', to='contenttypes.contenttype'),
        ),
    ]
