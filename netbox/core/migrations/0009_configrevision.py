from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_contenttype_proxy'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ConfigRevision',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                        ('created', models.DateTimeField(auto_now_add=True)),
                        ('comment', models.CharField(blank=True, max_length=200)),
                        ('data', models.JSONField(blank=True, null=True)),
                    ],
                    options={
                        'verbose_name': 'config revision',
                        'verbose_name_plural': 'config revisions',
                        'ordering': ['-created'],
                    },
                ),
            ],
            # Table will be renamed from extras_configrevision in extras/0101_move_configrevision
            database_operations=[],
        ),
    ]
