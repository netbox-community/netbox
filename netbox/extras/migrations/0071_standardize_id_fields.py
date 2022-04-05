from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('extras', '0070_customlink_enabled'),
    ]

    operations = [
        # Model IDs
        migrations.AlterField(
            model_name='configcontext',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='configrevision',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='customlink',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='exporttemplate',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='imageattachment',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='jobresult',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='taggeditem',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='webhook',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),

        # GFK IDs
        migrations.AlterField(
            model_name='imageattachment',
            name='object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='journalentry',
            name='assigned_object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='changed_object_id',
            field=models.PositiveBigIntegerField(),
        ),
        migrations.AlterField(
            model_name='objectchange',
            name='related_object_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
