from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0004_netboxgroup_netboxuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserToken',
            fields=[
            ],
            options={
                'verbose_name': 'token',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('users.token',),
        ),
    ]
