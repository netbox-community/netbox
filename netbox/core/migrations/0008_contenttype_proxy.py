import core.models.contenttypes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0007_job_add_error_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectType',
            fields=[],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('contenttypes.contenttype',),
            managers=[
                ('objects', core.models.contenttypes.ObjectTypeManager()),
            ],
        ),
    ]
