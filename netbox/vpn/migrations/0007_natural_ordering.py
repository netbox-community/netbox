from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('vpn', '0006_charfield_null_choices'),
        ('dcim', '0197_natural_sort_collation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ikepolicy',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ikeproposal',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecpolicy',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecprofile',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='ipsecproposal',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='l2vpn',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='tunnel',
            name='name',
            field=models.CharField(db_collation='natural_sort', max_length=100, unique=True),
        ),
    ]
