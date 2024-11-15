from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0016_charfield_null_choices'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
    ]
