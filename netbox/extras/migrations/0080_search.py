from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0079_jobresult_scheduled_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='search_weight',
            field=models.PositiveSmallIntegerField(default=1000),
        ),
        migrations.CreateModel(
            name='CachedValue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('field', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=30)),
                ('value', models.TextField(db_index=True)),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('weight', 'object_type', 'object_id'),
            },
        ),
    ]
