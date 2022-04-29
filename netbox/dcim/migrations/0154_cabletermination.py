from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0153_created_datetimefield'),
    ]

    operations = [
        migrations.CreateModel(
            name='CableTermination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('cable_end', models.CharField(max_length=1)),
                ('termination_id', models.PositiveBigIntegerField()),
                ('cable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terminations', to='dcim.cable')),
                ('termination_type', models.ForeignKey(limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'circuits'), ('model__in', ('circuittermination',))), models.Q(('app_label', 'dcim'), ('model__in', ('consoleport', 'consoleserverport', 'frontport', 'interface', 'powerfeed', 'poweroutlet', 'powerport', 'rearport'))), _connector='OR')), on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.AddConstraint(
            model_name='cabletermination',
            constraint=models.UniqueConstraint(fields=('termination_type', 'termination_id'), name='unique_termination'),
        ),
    ]
