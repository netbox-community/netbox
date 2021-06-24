from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0060_customlink_button_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='customfield',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customfield',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='customlink',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='customlink',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='created',
            field=models.DateField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='exporttemplate',
            name='last_updated',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
