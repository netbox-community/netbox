from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0046_alter_cluster__location_alter_cluster__region_and_more'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='virtualmachine',
            options={'ordering': ('name', 'pk')},
        ),
        migrations.AlterModelOptions(
            name='virtualdisk',
            options={'ordering': ('virtual_machine', 'name')},
        ),
        migrations.RemoveField(
            model_name='virtualmachine',
            name='_name',
        ),
        migrations.AlterField(
            model_name='virtualdisk',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=64),
        ),
        migrations.AlterField(
            model_name='cluster',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.RemoveField(
            model_name='virtualdisk',
            name='_name',
        ),
    ]
