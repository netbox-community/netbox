from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tenancy', '0018_contact_groups'),
    ]

    operations = [
        migrations.AddField(
            model_name='contactgroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='tenantgroup',
            name='comments',
            field=models.TextField(blank=True),
        ),
    ]
