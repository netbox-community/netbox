from django.db import migrations, models
import django.db.models.deletion

VIRTUALMACHINE_STATUS_CHOICES = (
    (0, 'offline'),
    (1, 'active'),
    (3, 'staged'),
)


def virtualmachine_status_to_slug(apps, schema_editor):
    VirtualMachine = apps.get_model('virtualization', 'VirtualMachine')
    for id, slug in VIRTUALMACHINE_STATUS_CHOICES:
        VirtualMachine.objects.filter(status=str(id)).update(status=slug)


class Migration(migrations.Migration):

    replaces = [('virtualization', '0010_cluster_add_tenant'), ('virtualization', '0011_3569_virtualmachine_fields'), ('virtualization', '0012_vm_name_nonunique')]

    dependencies = [
        ('tenancy', '0001_initial'),
        ('tenancy', '0006_custom_tag_models'),
        ('virtualization', '0009_custom_tag_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='cluster',
            name='tenant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='clusters', to='tenancy.Tenant'),
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='name',
            field=models.CharField(max_length=64),
        ),
        migrations.AlterUniqueTogether(
            name='virtualmachine',
            unique_together={('cluster', 'tenant', 'name')},
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=virtualmachine_status_to_slug,
        ),
    ]
