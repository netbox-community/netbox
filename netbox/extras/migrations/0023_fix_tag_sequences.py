from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0022_custom_links'),
    ]

    operations = [
        # Update the last_value for tag Tag and TaggedItem ID sequences
        migrations.RunSQL("SELECT setval('extras_tag_id_seq', (SELECT id FROM extras_tag ORDER BY id DESC LIMIT 1) + 1)"),
        migrations.RunSQL("SELECT setval('extras_taggeditem_id_seq', (SELECT id FROM extras_taggeditem ORDER BY id DESC LIMIT 1) + 1)"),
    ]
