import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('dcim', '0064_remove_platform_rpc_client'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontPort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('rear_port_position', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('description', models.CharField(blank=True, max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontports', to='dcim.Device')),
            ],
            options={
                'ordering': ['device', 'name'],
            },
        ),
        migrations.CreateModel(
            name='FrontPortTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('rear_port_position', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
            ],
            options={
                'ordering': ['device_type', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RearPort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('positions', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
                ('description', models.CharField(blank=True, max_length=100)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearports', to='dcim.Device')),
                ('tags', taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag')),
            ],
            options={
                'ordering': ['device', 'name'],
            },
        ),
        migrations.CreateModel(
            name='RearPortTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=64)),
                ('type', models.PositiveSmallIntegerField()),
                ('positions', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(64)])),
            ],
            options={
                'ordering': ['device_type', 'name'],
            },
        ),
        migrations.AddField(
            model_name='rearporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rearport_templates', to='dcim.DeviceType'),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontport_templates', to='dcim.DeviceType'),
        ),
        migrations.AddField(
            model_name='frontporttemplate',
            name='rear_port',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontport_templates', to='dcim.RearPortTemplate'),
        ),
        migrations.AddField(
            model_name='frontport',
            name='rear_port',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='frontports', to='dcim.RearPort'),
        ),
        migrations.AddField(
            model_name='frontport',
            name='tags',
            field=taggit.managers.TaggableManager(through='taggit.TaggedItem', to='taggit.Tag'),
        ),
        migrations.AlterUniqueTogether(
            name='rearporttemplate',
            unique_together={('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='rearport',
            unique_together={('device', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='frontporttemplate',
            unique_together={('rear_port', 'rear_port_position'), ('device_type', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='frontport',
            unique_together={('device', 'name'), ('rear_port', 'rear_port_position')},
        ),

        # Rename reverse relationships of component templates to DeviceType
        migrations.AlterField(
            model_name='consoleporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleport_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='consoleserverporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consoleserverport_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='poweroutlettemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='poweroutlet_templates', to='dcim.DeviceType'),
        ),
        migrations.AlterField(
            model_name='powerporttemplate',
            name='device_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='powerport_templates', to='dcim.DeviceType'),
        ),
    ]
