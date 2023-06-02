import sys
from django.db import migrations, models
from ipam.choices import VLANAssignmentTypeChoices


def populate_assignment_type_field(apps, schema_editor):
    VLAN = apps.get_model('ipam', 'VLAN')

    total_count = VLAN.objects.count()
    if 'test' not in sys.argv:
        print(f'\nUpdating {total_count} VLANs...')

    for row in VLAN.objects.all():
        if row.group:
            row.assignment_type = VLANAssignmentTypeChoices.VLAN_GROUP
        elif row.site:
            row.assignment_type = VLANAssignmentTypeChoices.SITE
        else:
            # Assign the default value if nothing else matches
            row.assignment_type = VLANAssignmentTypeChoices.VLAN_GROUP
        row.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0066_iprange_mark_utilized'),
    ]

    operations = [
        migrations.AddField(
            model_name='vlan',
            name='assignment_type',
            field=models.CharField(default='vlan_group', max_length=50),
        ),
        migrations.RunPython(populate_assignment_type_field),
    ]
