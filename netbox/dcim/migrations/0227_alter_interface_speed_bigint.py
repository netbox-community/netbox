from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0226_modulebay_rebuild_tree'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interface',
            name='speed',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
