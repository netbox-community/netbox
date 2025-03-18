import django.db.models.deletion
from django.db import migrations, models


def migrate_contact_groups(apps, schema_editor):
    Contacts = apps.get_model('tenancy', 'Contact')

    qs = Contacts.objects.filter(group__isnull=False)
    for contact in qs:
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
