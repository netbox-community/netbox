from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DummyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=20)),
                ('number', models.IntegerField(default=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
