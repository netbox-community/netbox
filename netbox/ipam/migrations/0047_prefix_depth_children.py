from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0046_set_vlangroup_scope_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='_children',
            field=models.PositiveBigIntegerField(default=0, editable=False),
        ),
        migrations.AddField(
            model_name='prefix',
            name='_depth',
            field=models.PositiveSmallIntegerField(default=0, editable=False),
        ),
    ]
