from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0004_standardize_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='config', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user'],
                'verbose_name': 'User Preferences',
                'verbose_name_plural': 'User Preferences'
            },
        ),
    ]
