from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0136_device_airflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='region',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='region',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='sitegroup',
            name='slug',
            field=models.SlugField(max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='location',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('site', 'parent', 'name'), name='dcim_location_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('site', 'name'), name='dcim_location_name'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(fields=('site', 'parent', 'slug'), name='dcim_location_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='location',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('site', 'slug'), name='dcim_location_slug'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='dcim_region_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('name',), name='dcim_region_name'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(fields=('parent', 'slug'), name='dcim_region_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='region',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('slug',), name='dcim_region_slug'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(fields=('parent', 'name'), name='dcim_sitegroup_parent_name'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('name',), name='dcim_sitegroup_name'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(fields=('parent', 'slug'), name='dcim_sitegroup_parent_slug'),
        ),
        migrations.AddConstraint(
            model_name='sitegroup',
            constraint=models.UniqueConstraint(condition=models.Q(('parent', None)), fields=('slug',), name='dcim_sitegroup_slug'),
        ),
    ]
