from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0063_webhook_conditions'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfigRevision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comment', models.CharField(blank=True, max_length=200)),
                ('data', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
