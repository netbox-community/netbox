from django.db import migrations

from extras.choices import JournalEntryKindChoices


def set_kind_default(apps, schema_editor):
    """
    Set kind to "info" on any entries with no kind assigned.
    """
    JournalEntry = apps.get_model('extras', 'JournalEntry')
    JournalEntry.objects.filter(kind='').update(kind=JournalEntryKindChoices.KIND_INFO)


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0122_charfield_null_choices'),
    ]

    operations = [
        migrations.RunPython(
            code=set_kind_default,
            reverse_code=migrations.RunPython.noop
        ),
    ]
