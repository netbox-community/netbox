from django.db import migrations, models


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
    atomic = False

    dependencies = [
        ('virtualization', '0010_cluster_add_tenant'),
    ]

    operations = [

        # VirtualMachine.status
        migrations.AlterField(
            model_name='virtualmachine',
            name='status',
            field=models.CharField(default='active', max_length=50),
        ),
        migrations.RunPython(
            code=virtualmachine_status_to_slug
        ),

    ]
