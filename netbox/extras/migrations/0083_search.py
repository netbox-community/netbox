import uuid

import django.db.models.deletion
import django.db.models.lookups
from django.db import migrations, models
import extras.fields


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0041_standardize_description_comments'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dcim', '0166_virtualdevicecontext'),
        ('extras', '0082_savedfilter'),
        ('ipam', '0063_standardize_description_comments'),
        ('tenancy', '0009_standardize_description_comments'),
        ('virtualization', '0034_standardize_description_comments'),
        ('wireless', '0008_wirelesslan_status'),
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
                ('value', extras.fields.CachedValueField()),
                ('weight', models.PositiveSmallIntegerField(default=1000)),
                ('object_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contenttypes.contenttype')),
            ],
            options={
                'ordering': ('weight', 'object_type', 'object_id'),
            },
        ),
    ]
