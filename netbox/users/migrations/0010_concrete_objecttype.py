from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_concrete_objecttype'),
        ('users', '0009_update_group_perms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ObjectPermission',
            name='object_types',
            field=models.ManyToManyField(related_name='object_permissions', to='core.objecttype'),
        ),
    ]
