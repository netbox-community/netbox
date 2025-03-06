import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0011_move_objectchange'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='object_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='jobs',
                to='contenttypes.contenttype',
            ),
        ),
    ]
