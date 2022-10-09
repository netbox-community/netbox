from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0038_cabling_cleanup'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='providernetwork',
            name='circuits_providernetwork_provider_name',
        ),
        migrations.AlterUniqueTogether(
            name='circuit',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='circuittermination',
            unique_together=set(),
        ),
        migrations.AlterUniqueTogether(
            name='providernetwork',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='circuit',
            constraint=models.UniqueConstraint(fields=('provider', 'cid'), name='circuits_circuit_unique_provider_cid'),
        ),
        migrations.AddConstraint(
            model_name='circuittermination',
            constraint=models.UniqueConstraint(fields=('circuit', 'term_side'), name='circuits_circuittermination_unique_circuit_term_side'),
        ),
        migrations.AddConstraint(
            model_name='providernetwork',
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_providernetwork_unique_provider_name'),
        ),
    ]
