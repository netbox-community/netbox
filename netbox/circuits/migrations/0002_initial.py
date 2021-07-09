from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dcim', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('circuits', '0001_initial'),
        ('extras', '0001_initial'),
        ('tenancy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='providernetwork',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='_cable_peer_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cable',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.cable'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='circuit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='circuits.circuit'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='provider_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='circuits.providernetwork'),
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='dcim.site'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provider'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='tenancy.tenant'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='termination_a',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='circuits.circuittermination'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='termination_z',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='circuits.circuittermination'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.circuittype'),
        ),
        migrations.AddConstraint(
            model_name='providernetwork',
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_providernetwork_provider_name'),
        ),
        migrations.AlterUniqueTogether(
            name='providernetwork',
            unique_together={('provider', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='circuittermination',
            unique_together={('circuit', 'term_side')},
        ),
        migrations.AlterUniqueTogether(
            name='circuit',
            unique_together={('provider', 'cid')},
        ),
    ]
