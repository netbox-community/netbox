import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0064_configrevision'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0051_extend_tag_support'),
    ]

    operations = [
        migrations.CreateModel(
            name='FHRPGroup',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('group_id', models.PositiveSmallIntegerField()),
                ('protocol', models.CharField(max_length=50)),
                ('auth_type', models.CharField(blank=True, max_length=50)),
                ('auth_key', models.CharField(blank=True, max_length=255)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'FHRP group',
                'ordering': ['protocol', 'group_id', 'pk'],
            },
        ),
        migrations.AlterField(
            model_name='ipaddress',
            name='assigned_object_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(models.Q(models.Q(('app_label', 'dcim'), ('model', 'interface')), models.Q(('app_label', 'ipam'), ('model', 'fhrpgroup')), models.Q(('app_label', 'virtualization'), ('model', 'vminterface')), _connector='OR')), null=True, on_delete=django.db.models.deletion.PROTECT, related_name='+', to='contenttypes.contenttype'),
        ),
        migrations.CreateModel(
            name='FHRPGroupAssignment',
            fields=[
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('priority', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ipam.fhrpgroup')),
            ],
            options={
                'verbose_name': 'FHRP group assignment',
                'ordering': ('priority', 'pk'),
                'unique_together': {('content_type', 'object_id', 'group')},
            },
        ),
    ]
