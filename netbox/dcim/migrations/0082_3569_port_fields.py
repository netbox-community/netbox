from django.db import migrations, models


PORT_TYPE_CHOICES = (
    (1000, '8p8c'),
    (1100, '110-punch'),
    (1200, 'bnc'),
    (2000, 'st'),
    (2100, 'sc'),
    (2110, 'sc-apc'),
    (2200, 'fc'),
    (2300, 'lc'),
    (2310, 'lc-apc'),
    (2400, 'mtrj'),
    (2500, 'mpo'),
    (2600, 'lsh'),
    (2610, 'lsh-apc'),
)


def frontporttemplate_type_to_slug(apps, schema_editor):
    FrontPortTemplate = apps.get_model('dcim', 'FrontPortTemplate')
    for id, slug in PORT_TYPE_CHOICES:
        FrontPortTemplate.objects.filter(type=id).update(type=slug)


def rearporttemplate_type_to_slug(apps, schema_editor):
    RearPortTemplate = apps.get_model('dcim', 'RearPortTemplate')
    for id, slug in PORT_TYPE_CHOICES:
        RearPortTemplate.objects.filter(type=id).update(type=slug)


def frontport_type_to_slug(apps, schema_editor):
    FrontPort = apps.get_model('dcim', 'FrontPort')
    for id, slug in PORT_TYPE_CHOICES:
        FrontPort.objects.filter(type=id).update(type=slug)


def rearport_type_to_slug(apps, schema_editor):
    RearPort = apps.get_model('dcim', 'RearPort')
    for id, slug in PORT_TYPE_CHOICES:
        RearPort.objects.filter(type=id).update(type=slug)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('dcim', '0082_3569_interface_fields'),
    ]

    operations = [

        # FrontPortTemplate.type
        migrations.AlterField(
            model_name='frontporttemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=frontporttemplate_type_to_slug
        ),

        # RearPortTemplate.type
        migrations.AlterField(
            model_name='rearporttemplate',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=rearporttemplate_type_to_slug
        ),

        # FrontPort.type
        migrations.AlterField(
            model_name='frontport',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=frontport_type_to_slug
        ),

        # RearPort.type
        migrations.AlterField(
            model_name='rearport',
            name='type',
            field=models.CharField(max_length=50),
        ),
        migrations.RunPython(
            code=rearport_type_to_slug
        ),
    ]
