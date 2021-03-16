import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


def replicate_ports(apps, schema_editor):
    Service = apps.get_model('ipam', 'Service')
    # TODO: Figure out how to cast IntegerField to an array so we can use .update()
    for service in Service.objects.all():
        Service.objects.filter(pk=service.pk).update(ports=[service.port])


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0038_custom_field_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='ports',
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.PositiveIntegerField(
                    validators=[
                        django.core.validators.MinValueValidator(1),
                        django.core.validators.MaxValueValidator(65535)
                    ]
                ),
                default=[],
                size=None
            ),
            preserve_default=False,
        ),

        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ('protocol', 'ports', 'pk')},
        ),
        migrations.RunPython(
            code=replicate_ports
        ),
    ]
