import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0118_customfield_uniqueness'),
        ('users', '0009_update_group_perms'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('groups', models.ManyToManyField(blank=True, related_name='notification_groups', to='users.group')),
                (
                    'users',
                    models.ManyToManyField(blank=True, related_name='notification_groups', to=settings.AUTH_USER_MODEL),
                ),
            ],
            options={
                'verbose_name': 'notification group',
                'verbose_name_plural': 'notification groups',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveBigIntegerField()),
                (
                    'object_type',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype'),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='subscriptions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'subscription',
                'verbose_name_plural': 'subscriptions',
                'ordering': ('-created', 'user'),
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('read', models.DateTimeField(blank=True, null=True)),
                ('object_id', models.PositiveBigIntegerField()),
                ('event_type', models.CharField(max_length=50)),
                (
                    'object_type',
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='contenttypes.contenttype'),
                ),
                ('object_repr', models.CharField(editable=False, max_length=200)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='notifications',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': 'notification',
                'verbose_name_plural': 'notifications',
                'ordering': ('-created', 'pk'),
                'indexes': [models.Index(fields=['object_type', 'object_id'], name='extras_noti_object__be74d5_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='notification',
            constraint=models.UniqueConstraint(
                fields=('object_type', 'object_id', 'user'), name='extras_notification_unique_per_object_and_user'
            ),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['object_type', 'object_id'], name='extras_subs_object__37ef68_idx'),
        ),
        migrations.AddConstraint(
            model_name='subscription',
            constraint=models.UniqueConstraint(
                fields=('object_type', 'object_id', 'user'), name='extras_subscription_unique_per_object_and_user'
            ),
        ),
    ]
