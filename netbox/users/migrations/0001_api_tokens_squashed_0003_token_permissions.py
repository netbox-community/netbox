import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [('users', '0001_api_tokens'), ('users', '0002_unicode_literals'), ('users', '0003_token_permissions')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('expires', models.DateTimeField(blank=True, null=True)),
                ('key', models.CharField(max_length=40, unique=True, validators=[django.core.validators.MinLengthValidator(40)])),
                ('write_enabled', models.BooleanField(default=True, help_text='Permit create/update/delete operations using this key')),
                ('description', models.CharField(blank=True, max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.AlterModelOptions(
            name='token',
            options={},
        ),
    ]
