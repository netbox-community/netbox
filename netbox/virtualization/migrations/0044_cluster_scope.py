import django.db.models.deletion
from django.db import migrations, models


def copy_site_assignments(apps, schema_editor):
     """
     Copy site ForeignKey values to the scope GFK.
     """
     ContentType = apps.get_model('contenttypes', 'ContentType')
     Cluster = apps.get_model('virtualization', 'Cluster')
     Site = apps.get_model('dcim', 'Site')

     Cluster.objects.filter(site__isnull=False).update(
         scope_type=ContentType.objects.get_for_model(Site),
         scope_id=models.F('site_id')
     )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('virtualization', '0043_qinq_svlan'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='scope_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='cluster',
            name='scope_type',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(('model__in', ('region', 'sitegroup', 'site', 'location'))),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype',
            ),
        ),

        # Copy over existing site assignments
        migrations.RunPython(
            code=copy_site_assignments,
            reverse_code=migrations.RunPython.noop
        ),

    ]
