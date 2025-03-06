import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0010_gfk_indexes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='ObjectChange',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                        ('time', models.DateTimeField(auto_now_add=True, db_index=True)),
                        ('user_name', models.CharField(editable=False, max_length=150)),
                        ('request_id', models.UUIDField(db_index=True, editable=False)),
                        ('action', models.CharField(max_length=50)),
                        ('changed_object_id', models.PositiveBigIntegerField()),
                        ('related_object_id', models.PositiveBigIntegerField(blank=True, null=True)),
                        ('object_repr', models.CharField(editable=False, max_length=200)),
                        ('prechange_data', models.JSONField(blank=True, editable=False, null=True)),
                        ('postchange_data', models.JSONField(blank=True, editable=False, null=True)),
                        (
                            'changed_object_type',
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='+',
                                to='contenttypes.contenttype',
                            ),
                        ),
                        (
                            'related_object_type',
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name='+',
                                to='contenttypes.contenttype',
                            ),
                        ),
                        (
                            'user',
                            models.ForeignKey(
                                blank=True,
                                null=True,
                                on_delete=django.db.models.deletion.SET_NULL,
                                related_name='changes',
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        'verbose_name': 'object change',
                        'verbose_name_plural': 'object changes',
                        'ordering': ['-time'],
                        'indexes': [
                            models.Index(
                                fields=['changed_object_type', 'changed_object_id'],
                                name='core_object_changed_c227ce_idx',
                            ),
                            models.Index(
                                fields=['related_object_type', 'related_object_id'],
                                name='core_object_related_3375d6_idx',
                            ),
                        ],
                    },
                ),
            ],
            # Table has been renamed from 'extras' app
            database_operations=[],
        ),
    ]
