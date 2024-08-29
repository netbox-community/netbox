from django.db import migrations, models


def update_link_buttons(apps, schema_editor):
    CustomLink = apps.get_model('extras', 'CustomLink')
    CustomLink.objects.filter(button_class='outline-dark').update(button_class='default')


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0115_convert_dashboard_widgets'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customlink',
            name='button_class',
            field=models.CharField(default='default', max_length=30),
        ),
        migrations.RunPython(
            code=update_link_buttons,
            reverse_code=migrations.RunPython.noop
        ),
    ]
