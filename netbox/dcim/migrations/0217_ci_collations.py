from django.contrib.postgres.operations import CreateCollation
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0216_poweroutlettemplate_color'),
    ]

    operations = [
        # Create a case-insensitive collation
        CreateCollation(
            'case_insensitive',
            provider='icu',
            locale='und-u-ks-level2',
            deterministic=False,
        ),
        # Create a case-insensitive collation with natural sorting
        CreateCollation(
            'ci_natural_sort',
            provider='icu',
            locale='und-u-kn-true-ks-level2',
            deterministic=False,
        ),
    ]
