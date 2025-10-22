import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0014_users_token_v2'),
    ]

    operations = [
        migrations.CreateModel(
            name='OwnerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'verbose_name': 'owner group',
                'verbose_name_plural': 'owner groups',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Owner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                (
                    'group',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name='members',
                        to='users.ownergroup',
                    ),
                ),
                (
                    'user_groups',
                    models.ManyToManyField(
                        blank=True,
                        related_name='owners',
                        related_query_name='owner',
                        to='users.group',
                    ),
                ),
                (
                    'users',
                    models.ManyToManyField(
                        blank=True,
                        related_name='owners',
                        related_query_name='owner',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'owner',
                'verbose_name_plural': 'owners',
                'ordering': ('name',),
            },
        ),
    ]
