from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('ipam', '0001_initial'),
        ('dcim', '0001_initial'),
        ('circuits', '0002_squashed'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='asns',
            field=models.ManyToManyField(blank=True, related_name='providers', to='ipam.asn'),
        ),
        migrations.AddField(
            model_name='provider',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuittype',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
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
            model_name='circuittermination',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provider'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='provider_account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuits', to='circuits.provideraccount'),
        ),
        migrations.AddField(
            model_name='circuit',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
