from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0001_initial'),
        ('virtualization', '0009_custom_tag_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='tenancy.Tenant'),
        ),
    ]
