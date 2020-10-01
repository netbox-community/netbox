import dcim.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0119_inventoryitem_mptt_rebuild'),
    ]

    operations = [
        migrations.CreateModel(
            name='CablePath',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('origin_id', models.PositiveIntegerField()),
                ('destination_id', models.PositiveIntegerField(blank=True, null=True)),
                ('path', dcim.fields.PathField(base_field=models.CharField(max_length=40), size=None)),
                ('destination_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
                ('origin_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
                ('is_connected', models.BooleanField(default=False)),
            ],
        ),
    ]
