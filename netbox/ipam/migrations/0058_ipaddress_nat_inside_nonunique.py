from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0057_created_datetimefield'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ipaddress',
            name='nat_inside',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='nat_outside', to='ipam.ipaddress'),
        ),
    ]
