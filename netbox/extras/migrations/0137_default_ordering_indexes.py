from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0022_default_ordering_indexes'),
        ('dcim', '0232_default_ordering_indexes'),
        ('extras', '0136_customfield_validation_schema'),
        ('tenancy', '0023_add_mptt_tree_indexes'),
        ('users', '0015_owner'),
        ('virtualization', '0054_virtualmachinetype'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='bookmark',
            index=models.Index(fields=['created', 'id'], name='extras_book_created_1cb4a5_idx'),
        ),
        migrations.AddIndex(
            model_name='configcontext',
            index=models.Index(fields=['weight', 'name'], name='extras_conf_weight_ef9a81_idx'),
        ),
        migrations.AddIndex(
            model_name='configtemplate',
            index=models.Index(fields=['name'], name='extras_conf_name_e276bf_idx'),
        ),
        migrations.AddIndex(
            model_name='customfield',
            index=models.Index(fields=['group_name', 'weight', 'name'], name='extras_cust_group_n_40cb93_idx'),
        ),
        migrations.AddIndex(
            model_name='customlink',
            index=models.Index(fields=['group_name', 'weight', 'name'], name='extras_cust_group_n_5a8be0_idx'),
        ),
        migrations.AddIndex(
            model_name='exporttemplate',
            index=models.Index(fields=['name'], name='extras_expo_name_55a9af_idx'),
        ),
        migrations.AddIndex(
            model_name='imageattachment',
            index=models.Index(fields=['name', 'id'], name='extras_imag_name_23cd9f_idx'),
        ),
        migrations.AddIndex(
            model_name='journalentry',
            index=models.Index(fields=['-created'], name='extras_jour_created_ec0fac_idx'),
        ),
        migrations.AddIndex(
            model_name='notification',
            index=models.Index(fields=['-created', 'id'], name='extras_noti_created_1d5146_idx'),
        ),
        migrations.AddIndex(
            model_name='savedfilter',
            index=models.Index(fields=['weight', 'name'], name='extras_save_weight_c070c4_idx'),
        ),
        migrations.AddIndex(
            model_name='script',
            index=models.Index(fields=['module', 'name'], name='extras_scri_module__8bd99c_idx'),
        ),
        migrations.AddIndex(
            model_name='subscription',
            index=models.Index(fields=['-created', 'user'], name='extras_subs_created_034618_idx'),
        ),
        migrations.AddIndex(
            model_name='tableconfig',
            index=models.Index(fields=['weight', 'name'], name='extras_tabl_weight_7c4bb6_idx'),
        ),
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['weight', 'name'], name='extras_tag_weight_d99f50_idx'),
        ),
    ]
