import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0058_journalentry'),
        ('circuits', '0026_mark_connected'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cloud',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='clouds', to='circuits.provider')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('provider', 'name'),
            },
        ),
        migrations.AddConstraint(
            model_name='cloud',
            constraint=models.UniqueConstraint(fields=('provider', 'name'), name='circuits_cloud_provider_name'),
        ),
        migrations.AlterUniqueTogether(
            name='cloud',
            unique_together={('provider', 'name')},
        ),
        migrations.AddField(
            model_name='circuittermination',
            name='cloud',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='circuits.cloud'),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='circuit_terminations', to='dcim.site'),
        ),
    ]
