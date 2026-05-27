import django.db.models.deletion
import mptt.fields
import taggit.managers
from django.db import migrations, models

import utilities.json


class Migration(migrations.Migration):
    replaces = [
        ('tenancy', '0002_tenant_ordering'),
        ('tenancy', '0003_contacts'),
        ('tenancy', '0004_extend_tag_support'),
        ('tenancy', '0005_standardize_id_fields'),
        ('tenancy', '0006_created_datetimefield'),
        ('tenancy', '0007_contact_link'),
        ('tenancy', '0008_unique_constraints'),
        ('tenancy', '0009_standardize_description_comments'),
        ('tenancy', '0010_tenant_relax_uniqueness'),
        ('tenancy', '0011_contactassignment_tags'),
    ]

    dependencies = [
        ('extras', '0002_squashed_0059'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('tenancy', '0001_squashed_0012'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tenant',
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ContactGroup',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                (
                    'parent',
                    mptt.fields.TreeForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='children',
                        to='tenancy.contactgroup',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'ordering': ['name'],
                'unique_together': set(),
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                (
                    'custom_field_data',
                    models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder),
                ),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                (
                    'group',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='contacts',
                        to='tenancy.contactgroup',
                    ),
                ),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
                ('link', models.URLField(blank=True)),
            ],
            options={
                'ordering': ['name'],
                'unique_together': set(),
            },
        ),
        migrations.AddField(
            model_name='tenantgroup',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='tenantgroup',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.CreateModel(
            name='ContactAssignment',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('object_id', models.PositiveBigIntegerField()),
                ('priority', models.CharField(blank=True, max_length=50)),
                (
                    'contact',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='tenancy.contact'
                    ),
                ),
                (
                    'content_type',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
                ),
                (
                    'role',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='assignments',
                        to='tenancy.contactrole',
                    ),
                ),
            ],
            options={
                'ordering': ('priority', 'contact'),
                'unique_together': set(),
            },
        ),
        migrations.AddConstraint(
            model_name='contact',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='tenancy_contact_unique_group_name'),
        ),
        migrations.AddConstraint(
            model_name='contactassignment',
            constraint=models.UniqueConstraint(
                fields=('content_type', 'object_id', 'contact', 'role'),
                name='tenancy_contactassignment_unique_object_contact_role',
            ),
        ),
        migrations.AddConstraint(
            model_name='contactgroup',
            constraint=models.UniqueConstraint(
                fields=('parent', 'name'), name='tenancy_contactgroup_unique_parent_name'
            ),
        ),
        migrations.AddField(
            model_name='contact',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='tenant',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                fields=('group', 'name'),
                name='tenancy_tenant_unique_group_name',
                violation_error_message='Tenant name must be unique per group.',
            ),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                condition=models.Q(('group__isnull', True)), fields=('name',), name='tenancy_tenant_unique_name'
            ),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                fields=('group', 'slug'),
                name='tenancy_tenant_unique_group_slug',
                violation_error_message='Tenant slug must be unique per group.',
            ),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(
                condition=models.Q(('group__isnull', True)), fields=('slug',), name='tenancy_tenant_unique_slug'
            ),
        ),
        migrations.AddField(
            model_name='contactassignment',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
    ]
