import django.db.models.deletion
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('secrets', '0001_initial'), ('secrets', '0002_userkey_add_session_key'), ('secrets', '0003_unicode_literals'), ('secrets', '0004_tags'), ('secrets', '0005_change_logging'), ('secrets', '0006_custom_tag_models')]

    dependencies = [
        ('dcim', '0002_auto_20160622_1821'),
        ('extras', '0019_tag_taggeditem'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecretRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('groups', models.ManyToManyField(blank=True, related_name='secretroles', to='auth.Group')),
                ('users', models.ManyToManyField(blank=True, related_name='secretroles', to=settings.AUTH_USER_MODEL)),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('public_key', models.TextField(verbose_name='RSA public key')),
                ('master_key_cipher', models.BinaryField(blank=True, max_length=512, null=True)),
                ('user', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='user_key', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__username'],
                'permissions': (('activate_userkey', 'Can activate user keys for decryption'),),
            },
        ),
        migrations.CreateModel(
            name='SessionKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cipher', models.BinaryField(max_length=512)),
                ('hash', models.CharField(editable=False, max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('userkey', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='session_key', to='secrets.UserKey')),
            ],
            options={
                'ordering': ['userkey__user__username'],
            },
        ),
        migrations.CreateModel(
            name='Secret',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('ciphertext', models.BinaryField(max_length=65568)),
                ('hash', models.CharField(editable=False, max_length=128)),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='secrets', to='dcim.Device')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='secrets', to='secrets.SecretRole')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='extras.TaggedItem', to='extras.Tag', verbose_name='Tags')),
            ],
            options={
                'ordering': ['device', 'role', 'name'],
                'unique_together': {('device', 'role', 'name')},
            },
        ),
    ]
