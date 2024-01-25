import django.contrib.auth.models
import django.contrib.postgres.fields
from django.db import migrations, models
import ipam.fields


class Migration(migrations.Migration):

    replaces = [
        ('users', '0002_standardize_id_fields'),
        ('users', '0003_token_allowed_ips_last_used'),
        ('users', '0004_netboxgroup_netboxuser')
    ]

    dependencies = [
        ('users', '0001_squashed_0011'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='objectpermission',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='token',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='userconfig',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='token',
            name='allowed_ips',
            field=django.contrib.postgres.fields.ArrayField(base_field=ipam.fields.IPNetworkField(), blank=True, null=True, size=None),
        ),
        migrations.AddField(
            model_name='token',
            name='last_used',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='NetBoxGroup',
            fields=[
            ],
            options={
                'verbose_name': 'Group',
                'proxy': True,
                'indexes': [],
                'constraints': [],
                'ordering': ('name',),
            },
            bases=('auth.group',),
            managers=[
                ('objects', django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='NetBoxUser',
            fields=[
            ],
            options={
                'verbose_name': 'User',
                'proxy': True,
                'indexes': [],
                'constraints': [],
                'ordering': ('username',),
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
