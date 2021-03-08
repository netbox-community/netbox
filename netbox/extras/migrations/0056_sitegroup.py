from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0130_sitegroup'),
        ('extras', '0055_objectchange_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='configcontext',
            name='site_groups',
            field=models.ManyToManyField(blank=True, related_name='_extras_configcontext_site_groups_+', to='dcim.SiteGroup'),
        ),
    ]
