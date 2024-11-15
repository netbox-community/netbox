from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0196_qinq_svlan'),
    ]

    operations = [
        CreateCollation(
            "natural_sort",
            provider="icu",
            locale="und-u-kn-true",
        ),
    ]
