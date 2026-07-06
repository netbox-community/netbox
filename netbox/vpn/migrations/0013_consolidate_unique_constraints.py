from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('tenancy', '0026_consolidate_unique_constraints'),
        ('users', '0016_default_ordering_indexes'),
        ('vpn', '0012_default_ordering_indexes'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='tunnel',
            name='vpn_tunnel_group_name',
        ),
        migrations.RemoveConstraint(
            model_name='tunnel',
            name='vpn_tunnel_name',
        ),
    ]
