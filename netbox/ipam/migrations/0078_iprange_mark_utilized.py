from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipam', '0077_vlangroup_tenant'),
    ]

    operations = [
        migrations.AddField(
            model_name='iprange',
            name='mark_populated',
            field=models.BooleanField(default=False),
        ),
    ]
