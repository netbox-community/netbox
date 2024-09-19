from django.db import migrations


def rebuild_mptt(apps, schema_editor):
    from dcim.models import ModuleBay
    ModuleBay.objects.rebuild()


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0190_nested_modules'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_mptt,
            reverse_code=migrations.RunPython.noop
        ),
    ]
