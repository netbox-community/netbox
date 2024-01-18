from django.conf import settings
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import ipam.fields
import users.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    replaces = [
        # Squashed for v3.0
        ('users', '0001_api_tokens'),
        ('users', '0002_unicode_literals'),
        ('users', '0003_token_permissions'),
        ('users', '0004_standardize_description'),
        ('users', '0005_userconfig'),
        ('users', '0006_create_userconfigs'),
        ('users', '0007_proxy_group_user'),
        ('users', '0008_objectpermission'),
        ('users', '0009_replicate_permissions'),
        ('users', '0010_update_jsonfield'),
        ('users', '0011_standardize_models'),

        # Squashed for v4.0
        ('users', '0002_standardize_id_fields'),
        ('users', '0003_token_allowed_ips_last_used'),
        ('users', '0004_netboxgroup_netboxuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='NetBoxGroup',
            fields=[
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
                'ordering': ('name',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.group',),
            managers=[
                ('objects', users.models.NetBoxGroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='NetBoxUser',
            fields=[
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'ordering': ('username',),
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('auth.user',),
            managers=[
                ('objects', users.models.NetBoxUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data', models.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'user preferences',
                'verbose_name_plural': 'user preferences',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('last_used', models.DateTimeField(blank=True, null=True)),
                ('key', models.CharField(max_length=40, unique=True, validators=[django.core.validators.MinLengthValidator(40)])),
                ('write_enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('allowed_ips', django.contrib.postgres.fields.ArrayField(base_field=ipam.fields.IPNetworkField(), blank=True, null=True, size=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'token',
                'verbose_name_plural': 'tokens',
            },
        ),
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('enabled', models.BooleanField(default=True)),
                ('actions', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=None)),
                ('constraints', models.JSONField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='object_permissions', to='auth.group')),
                ('object_types', models.ManyToManyField(limit_choices_to=models.Q(models.Q(models.Q(('app_label__in', ['account', 'admin', 'auth', 'contenttypes', 'sessions', 'taggit', 'users']), _negated=True), models.Q(('app_label', 'auth'), ('model__in', ['group', 'user'])), models.Q(('app_label', 'users'), ('model__in', ['objectpermission', 'token'])), _connector='OR')), related_name='object_permissions', to='contenttypes.contenttype')),
                ('users', models.ManyToManyField(blank=True, related_name='object_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'permission',
                'verbose_name_plural': 'permissions',
                'ordering': ['name'],
            },
        ),
    ]
