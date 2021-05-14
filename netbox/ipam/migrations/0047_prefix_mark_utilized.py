from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0046_set_vlangroup_scope_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='mark_utilized',
            field=models.BooleanField(default=False),
        ),
    ]
