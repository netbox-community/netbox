import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dcim', '0250_cooling_infrastructure'),
        ('dummy_plugin', '0002_dummynetboxmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='DummySiteAttachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                (
                    'site',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='dummy_site_attachments',
                        to='dcim.site',
                    ),
                ),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
