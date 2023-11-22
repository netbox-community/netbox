from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0100_customfield_ui_attrs'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.DeleteModel(
                    name='ConfigRevision',
                ),
            ],
            database_operations=[
                migrations.AlterModelTable(
                    name='ConfigRevision',
                    table='core_configrevision',
                ),
            ],
        ),
    ]
