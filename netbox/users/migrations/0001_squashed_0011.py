from django.conf import settings
import django.contrib.auth.models
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import users.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    replaces = [
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
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(blank=True, null=True)),
                ('is_superuser', models.BooleanField(default=False)),
                (
                    'username',
                    models.CharField(
                        error_messages={'unique': 'A user with that username already exists.'},
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                    ),
                ),
                ('first_name', models.CharField(blank=True, max_length=150)),
                ('last_name', models.CharField(blank=True, max_length=150)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                (
                    'groups',
                    models.ManyToManyField(
                        blank=True, related_name='user_set', related_query_name='user', to='auth.group'
                    ),
                ),
                (
                    'user_permissions',
                    models.ManyToManyField(
                        blank=True, related_name='user_set', related_query_name='user', to='auth.permission'
                    ),
                ),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'auth_user',
                'ordering': ('username',),
            },
            managers=[
                ('objects', users.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data', models.JSONField(default=dict)),
                (
                    'user',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name='config', to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                'verbose_name': 'User Preferences',
                'verbose_name_plural': 'User Preferences',
                'ordering': ['user'],
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                (
                    'key',
                    models.CharField(
                        max_length=40, unique=True, validators=[django.core.validators.MinLengthValidator(40)]
                    ),
                ),
                ('write_enabled', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('enabled', models.BooleanField(default=True)),
                (
                    'actions',
                    django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30), size=None),
                ),
                ('constraints', models.JSONField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='object_permissions', to='auth.Group')),
                (
                    'object_types',
                    models.ManyToManyField(
                        limit_choices_to=models.Q(
                            models.Q(
                                models.Q(
                                    (
                                        'app_label__in',
                                        ['account', 'admin', 'auth', 'contenttypes', 'sessions', 'taggit', 'users'],
                                    ),
                                    _negated=True,
                                ),
                                models.Q(('app_label', 'auth'), ('model__in', ['group', 'user'])),
                                models.Q(('app_label', 'users'), ('model__in', ['objectpermission', 'token'])),
                                _connector='OR',
                            )
                        ),
                        related_name='object_permissions',
                        to='contenttypes.ContentType',
                    ),
                ),
                (
                    'users',
                    models.ManyToManyField(blank=True, related_name='object_permissions', to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                'verbose_name': 'permission',
                'ordering': ['name'],
            },
        ),
    ]
