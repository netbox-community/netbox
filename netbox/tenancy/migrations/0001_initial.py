from django.db import migrations, models
import django.db.models.deletion
import mptt.fields
import taggit.managers
import utilities.json


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('extras', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    replaces = [
        # Squashed for v3.0
        ('tenancy', '0002_tenant_group_optional'),
        ('tenancy', '0003_unicode_literals'),
        ('tenancy', '0004_tags'),
        ('tenancy', '0005_change_logging'),
        ('tenancy', '0006_custom_tag_models'),
        ('tenancy', '0007_nested_tenantgroups'),
        ('tenancy', '0008_nested_tenantgroups_rebuild'),
        ('tenancy', '0009_standardize_description'),
        ('tenancy', '0010_custom_field_data'),
        ('tenancy', '0011_standardize_name_length'),
        ('tenancy', '0012_standardize_models'),

        # Squashed for v4.0
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

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('title', models.CharField(blank=True, max_length=100)),
                ('phone', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('address', models.CharField(blank=True, max_length=200)),
                ('link', models.URLField(blank=True)),
            ],
            options={
                'verbose_name': 'contact',
                'verbose_name_plural': 'contacts',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='TenantGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tenancy.tenantgroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'tenant group',
                'verbose_name_plural': 'tenant groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Tenant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('comments', models.TextField(blank=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('group', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tenants', to='tenancy.tenantgroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'tenant',
                'verbose_name_plural': 'tenants',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ContactRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'contact role',
                'verbose_name_plural': 'contact roles',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='ContactGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='tenancy.contactgroup')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'contact group',
                'verbose_name_plural': 'contact groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ContactAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('priority', models.CharField(blank=True, max_length=50)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='tenancy.contact')),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assignments', to='tenancy.contactrole')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'contact assignment',
                'verbose_name_plural': 'contact assignments',
                'ordering': ('priority', 'contact'),
            },
        ),
        migrations.AddField(
            model_name='contact',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contacts', to='tenancy.contactgroup'),
        ),
        migrations.AddField(
            model_name='contact',
            name='tags',
            field=taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag'),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='tenancy_tenant_unique_group_name', violation_error_message='Tenant name must be unique per group.'),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(condition=models.Q(('group__isnull', True)), fields=('name',), name='tenancy_tenant_unique_name'),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(fields=('group', 'slug'), name='tenancy_tenant_unique_group_slug', violation_error_message='Tenant slug must be unique per group.'),
        ),
        migrations.AddConstraint(
            model_name='tenant',
            constraint=models.UniqueConstraint(condition=models.Q(('group__isnull', True)), fields=('slug',), name='tenancy_tenant_unique_slug'),
        ),
        migrations.AddConstraint(
            model_name='contactgroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='tenancy_contactgroup_unique_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='contactassignment',
            constraint=models.UniqueConstraint(fields=('content_type', 'object_id', 'contact', 'role'), name='tenancy_contactassignment_unique_object_contact_role'),
        ),
        migrations.AddConstraint(
            model_name='contact',
            constraint=models.UniqueConstraint(fields=('group', 'name'), name='tenancy_contact_unique_group_name'),
        ),
    ]
