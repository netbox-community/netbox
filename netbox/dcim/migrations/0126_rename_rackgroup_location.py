from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0125_console_port_speed'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RackGroup',
            new_name='Location',
        ),
        migrations.AlterModelOptions(
            name='rack',
            options={'ordering': ('site', 'location', '_name', 'pk')},
        ),
        migrations.AlterField(
            model_name='location',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='dcim.site'),
        ),
        migrations.RenameField(
            model_name='powerpanel',
            old_name='rack_group',
            new_name='location',
        ),
        migrations.RenameField(
            model_name='rack',
            old_name='group',
            new_name='location',
        ),
        migrations.AlterUniqueTogether(
            name='rack',
            unique_together={('location', 'facility_id'), ('location', 'name')},
        ),
    ]
