from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('ipam', '0044_standardize_models'),
    ]

    operations = [
        migrations.RenameField(
            model_name='vlangroup',
            old_name='site',
            new_name='scope_id',
        ),
        migrations.AlterField(
            model_name='vlangroup',
            name='scope_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vlangroup',
            name='scope_type',
            field=models.ForeignKey(blank=True, limit_choices_to=models.Q(model__in=('region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster')), null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterModelOptions(
            name='vlangroup',
            options={'ordering': ('name', 'pk'), 'verbose_name': 'VLAN group', 'verbose_name_plural': 'VLAN groups'},
        ),
        migrations.AlterUniqueTogether(
            name='vlangroup',
            unique_together={('scope_type', 'scope_id', 'name'), ('scope_type', 'scope_id', 'slug')},
        ),
    ]
