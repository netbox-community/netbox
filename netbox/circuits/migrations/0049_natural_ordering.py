from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0048_circuitterminations_cached_relations'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='providernetwork',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100),
        ),
    ]
