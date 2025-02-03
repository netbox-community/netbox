from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0075_vlan_qinq'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asnrange',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='routetarget',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=21, unique=True),
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='vrf',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
    ]
