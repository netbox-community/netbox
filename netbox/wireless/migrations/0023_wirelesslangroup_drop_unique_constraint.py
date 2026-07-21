from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('extras', '0139_alter_customfieldchoiceset_extra_choices'),
        ('users', '0016_default_ordering_indexes'),
        ('wireless', '0022_denormalization_triggers'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='wirelesslangroup',
            name='wireless_wirelesslangroup_unique_parent_name',
        ),
    ]
