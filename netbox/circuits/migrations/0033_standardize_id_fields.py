from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circuits', '0032_provider_service_id'),
    ]

    operations = [
        # Model IDs
        migrations.AlterField(
            model_name='circuit',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittermination',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='circuittype',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='provider',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='providernetwork',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False),
        ),

        # GFK IDs
        migrations.AlterField(
            model_name='circuittermination',
            name='_link_peer_id',
            field=models.PositiveBigIntegerField(blank=True, null=True),
        ),
    ]
