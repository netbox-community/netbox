from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('virtualization', '0038_virtualdisk'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='serial',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
