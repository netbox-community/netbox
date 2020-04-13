from django.db import migrations


def rebuild_mptt(apps, schema_editor):
    TenantGroup = apps.get_model('tenancy', 'TenantGroup')
    for i, tenantgroup in enumerate(TenantGroup.objects.all(), start=1):
        TenantGroup.objects.filter(pk=tenantgroup.pk).update(tree_id=i)


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0007_nested_tenantgroups'),
    ]

    operations = [
        migrations.RunPython(
            code=rebuild_mptt,
            reverse_code=migrations.RunPython.noop
        ),
    ]
