import django.db.models.deletion
from django.db import migrations, models


def migrate_contact_groups(apps, schema_editor):
    Contact = apps.get_model('tenancy', 'Contact')
    db_alias = schema_editor.connection.alias

    for contact in Contact.objects.using(db_alias).filter(group__isnull=False):
        contact.groups.add(contact.group)


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0017_natural_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactGroupMembership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ],
            options={
                'verbose_name': 'contact group membership',
                'verbose_name_plural': 'contact group memberships',
            },
        ),
        migrations.RemoveConstraint(
            model_name='contact',
            name='tenancy_contact_unique_group_name',
        ),
        migrations.AddField(
            model_name='contactgroupmembership',
            name='contact',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='+', to='tenancy.contact'
            ),
        ),
        migrations.AddField(
            model_name='contactgroupmembership',
            name='group',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name='+', to='tenancy.contactgroup'
            ),
        ),
        migrations.AddField(
            model_name='contact',
            name='groups',
            field=models.ManyToManyField(
                blank=True,
                related_name='contacts',
                related_query_name='contact',
                through='tenancy.ContactGroupMembership',
                to='tenancy.contactgroup',
            ),
        ),
        migrations.AddConstraint(
            model_name='contactgroupmembership',
            constraint=models.UniqueConstraint(fields=('group', 'contact'), name='unique_group_name'),
        ),
        migrations.RunPython(code=migrate_contact_groups, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='contact',
            name='group',
        ),
    ]


def oc_contact_groups(objectchange, reverting):
    for data in (objectchange.prechange_data, objectchange.postchange_data):
        if data is None:
            continue
        # Set the M2M field `groups` to a list containing the group ID
        data['groups'] = [data['group']] if data.get('group') else []
        data.pop('group', None)


objectchange_migrators = {
    'tenancy.contact': oc_contact_groups,
}
