from django.db import migrations, models
import django.db.models.deletion
import extras.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('extras', '0021_add_color_comments_changelog_to_tag'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('text', models.CharField(max_length=500)),
                ('url', models.CharField(max_length=500)),
                ('weight', models.PositiveSmallIntegerField(default=100)),
                ('group_name', models.CharField(blank=True, max_length=50)),
                ('button_class', models.CharField(default='default', max_length=30)),
                ('new_window', models.BooleanField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'ordering': ['group_name', 'weight', 'name'],
            },
        ),

        # Update limit_choices_to for CustomFields, ExportTemplates, and Webhooks
        migrations.AlterField(
            model_name='customfield',
            name='obj_type',
            field=models.ManyToManyField(related_name='custom_fields', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='obj_type',
            field=models.ManyToManyField(related_name='webhooks', to='contenttypes.ContentType'),
        ),
    ]
