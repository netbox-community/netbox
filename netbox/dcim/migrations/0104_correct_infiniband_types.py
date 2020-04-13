from django.db import migrations


INFINIBAND_SLUGS = (
    ('inifiband-sdr', 'infiniband-sdr'),
    ('inifiband-ddr', 'infiniband-ddr'),
    ('inifiband-qdr', 'infiniband-qdr'),
    ('inifiband-fdr10', 'infiniband-fdr10'),
    ('inifiband-fdr', 'infiniband-fdr'),
    ('inifiband-edr', 'infiniband-edr'),
    ('inifiband-hdr', 'infiniband-hdr'),
    ('inifiband-ndr', 'infiniband-ndr'),
    ('inifiband-xdr', 'infiniband-xdr'),
)


def correct_infiniband_types(apps, schema_editor):
    Interface = apps.get_model('dcim', 'Interface')
    for old, new in INFINIBAND_SLUGS:
        Interface.objects.filter(type=old).update(type=new)


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0103_standardize_description'),
    ]

    operations = [
        migrations.RunPython(
            code=correct_infiniband_types,
            reverse_code=migrations.RunPython.noop
        ),
    ]
