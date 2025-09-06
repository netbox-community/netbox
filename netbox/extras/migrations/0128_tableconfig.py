import django.contrib.postgres.fields
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0015_remove_redundant_indexes'),
        ('extras', '0127_configtemplate_as_attachment_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TableConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('table', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('enabled', models.BooleanField(default=True)),
                ('shared', models.BooleanField(default=True)),
                (
                    'columns',
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=100), size=None),
                ),
                (
                    'ordering',
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=100), blank=True, null=True, size=None
                    ),
                ),
                (
                    'object_type',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='table_configs',
                        to='contenttypes.contenttype'
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                'verbose_name': 'table config',
                'verbose_name_plural': 'table configs',
                'ordering': ('weight', 'name'),
            },
        ),
    ]
