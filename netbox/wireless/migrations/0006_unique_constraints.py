from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0005_wirelesslink_interface_types'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wirelesslangroup',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='wirelesslink',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='wirelesslangroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='wireless_wirelesslangroup_unique_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='wirelesslink',
            constraint=models.UniqueConstraint(fields=('interface_a', 'interface_b'), name='wireless_wirelesslink_unique_interfaces'),
        ),
    ]
