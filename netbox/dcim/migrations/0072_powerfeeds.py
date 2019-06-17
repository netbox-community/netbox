import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0021_add_color_comments_changelog_to_tag'),
        ('dcim', '0071_device_components_add_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='PowerFeed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('status', models.PositiveSmallIntegerField(default=1)),
                ('type', models.PositiveSmallIntegerField(default=1)),
                ('supply', models.PositiveSmallIntegerField(default=1)),
                ('phase', models.PositiveSmallIntegerField(default=1)),
                ('voltage', models.PositiveSmallIntegerField(default=120, validators=[django.core.validators.MinValueValidator(1)])),
                ('amperage', models.PositiveSmallIntegerField(default=20, validators=[django.core.validators.MinValueValidator(1)])),
                ('max_utilization', models.PositiveSmallIntegerField(default=80, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(100)])),
                ('available_power', models.PositiveSmallIntegerField(default=0, editable=False)),
                ('comments', models.TextField(blank=True)),
                ('cable', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.Cable')),
            ],
            options={
                'ordering': ['power_panel', 'name'],
            },
        ),
        migrations.CreateModel(
            name='PowerPanel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=50)),
                ('rack_group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.RackGroup')),
                ('site', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dcim.Site')),
            ],
            options={
                'ordering': ['site', 'name'],
            },
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='power_panel',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='powerfeeds', to='dcim.PowerPanel'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='rack',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='dcim.Rack'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='connected_endpoint',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.PowerPort'),
        ),
        migrations.AddField(
            model_name='powerfeed',
            name='connection_status',
            field=models.NullBooleanField(),
        ),
        migrations.RenameField(
            model_name='powerport',
            old_name='connected_endpoint',
            new_name='_connected_poweroutlet',
        ),
        migrations.AddField(
            model_name='powerport',
            name='_connected_powerfeed',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='dcim.PowerFeed'),
        ),
        migrations.AddField(
            model_name='powerport',
            name='allocated_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerport',
            name='maximum_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='allocated_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='powerporttemplate',
            name='maximum_draw',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterUniqueTogether(
            name='powerpanel',
            unique_together={('site', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='powerfeed',
            unique_together={('power_panel', 'name')},
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='feed_leg',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlet',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlets', to='dcim.PowerPort'),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='feed_leg',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poweroutlettemplate',
            name='power_port',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='poweroutlet_templates', to='dcim.PowerPortTemplate'),
        ),
    ]
