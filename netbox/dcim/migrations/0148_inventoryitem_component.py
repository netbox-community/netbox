from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0147_inventoryitemrole'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventoryitem',
            name='component_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='component_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(('app_label', 'dcim'), ('model__in', ('consoleport', 'consoleserverport', 'frontport', 'interface', 'poweroutlet', 'powerport', 'rearport'))), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
    ]
