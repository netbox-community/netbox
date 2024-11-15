from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wireless', '0011_wirelesslan__location_wirelesslan__region_and_more'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wirelesslangroup',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
    ]
