from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_gfk_indexes'),
        ('extras', '0111_rename_content_types'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='object_types',
            field=models.ManyToManyField(blank=True, related_name='+', to='core.objecttype'),
        ),
    ]
