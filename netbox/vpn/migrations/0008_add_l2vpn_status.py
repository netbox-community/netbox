from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vpn', '0007_natural_ordering'),
    ]

    operations = [
        migrations.AddField(
            model_name='l2vpn',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
    ]
