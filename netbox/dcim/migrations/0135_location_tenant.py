from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0002_tenant_ordering'),
        ('dcim', '0134_interface_wwn'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='locations', to='tenancy.tenant'),
        ),
    ]
