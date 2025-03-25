import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0077_vlangroup_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='parent_object_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='service',
            name='parent_object_type',
            field=models.ForeignKey(
                blank=True,
                limit_choices_to=models.Q(
                    models.Q(
                        models.Q(('app_label', 'dcim'), ('model', 'device')),
                        models.Q(('app_label', 'ipam'), ('model', 'fhrpgroup')),
                        models.Q(('app_label', 'virtualization'), ('model', 'virtualmachine')),
                        _connector='OR'
                    )
                ),
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='+',
                to='contenttypes.contenttype'
            ),
        ),
    ]
