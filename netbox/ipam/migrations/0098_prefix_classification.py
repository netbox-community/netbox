from django.db import migrations, models

# Frozen copy of the ipam.constants rules. A later change replaces the function in a new migration.
CLASSIFICATION_CASE = """CASE
    WHEN prefix <<= ANY (ARRAY[
        '192.0.0.9/32', '192.0.0.10/32', '64:ff9b::/96', '2001:1::1/128', '2001:1::2/127', '2001:3::/32',
        '2001:4:112::/48', '2001:20::/27'
    ]::cidr[]) THEN 'public'
    WHEN prefix <<= ANY (ARRAY['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', 'fc00::/7']::cidr[]) THEN 'private'
    WHEN prefix <<= ANY (ARRAY['100.64.0.0/10']::cidr[]) THEN 'shared'
    WHEN prefix <<= ANY (ARRAY['127.0.0.0/8', '::1/128']::cidr[]) THEN 'loopback'
    WHEN prefix <<= ANY (ARRAY['169.254.0.0/16', 'fe80::/10']::cidr[]) THEN 'link-local'
    WHEN prefix <<= ANY (ARRAY[
        '192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24', '2001:db8::/32', '3fff::/20'
    ]::cidr[]) THEN 'documentation'
    WHEN prefix <<= ANY (ARRAY['224.0.0.0/4', 'ff00::/8']::cidr[]) THEN 'multicast'
    WHEN prefix <<= ANY (ARRAY['198.18.0.0/15', '2001:2::/48']::cidr[]) THEN 'benchmarking'
    WHEN prefix <<= ANY (ARRAY[
        '0.0.0.0/8', '192.0.0.0/24', '192.88.99.0/24', '240.0.0.0/4', '::/3', '2001::/23', '2002::/16',
        '4000::/2', '8000::/2', 'c000::/3', 'e000::/4', 'f000::/5', 'f800::/6', 'fe00::/9', 'fec0::/10'
    ]::cidr[]) THEN 'special'
    ELSE 'public'
END"""


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0097_merge_ipaddress_host_index_and_multi_protocol_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='_classification',
            field=models.CharField(db_index=True, default='public', editable=False, max_length=50),
        ),
        migrations.RunSQL(
            sql=[
                'CREATE OR REPLACE FUNCTION ipam_prefix_classification(prefix cidr) RETURNS text '
                f'LANGUAGE sql IMMUTABLE AS $$ SELECT {CLASSIFICATION_CASE} $$',
                """
                CREATE OR REPLACE FUNCTION ipam_prefix_classification_fn() RETURNS trigger LANGUAGE plpgsql AS $$
                BEGIN
                    NEW._classification := ipam_prefix_classification(NEW.prefix);
                    RETURN NEW;
                END
                $$
                """,
                'DROP TRIGGER IF EXISTS ipam_prefix_classification ON ipam_prefix',
                """
                CREATE TRIGGER ipam_prefix_classification
                    BEFORE INSERT OR UPDATE OF prefix, _classification ON ipam_prefix
                    FOR EACH ROW EXECUTE FUNCTION ipam_prefix_classification_fn()
                """,
            ],
            reverse_sql=[
                'DROP TRIGGER IF EXISTS ipam_prefix_classification ON ipam_prefix',
                'DROP FUNCTION IF EXISTS ipam_prefix_classification_fn()',
                'DROP FUNCTION IF EXISTS ipam_prefix_classification(cidr)',
            ],
        ),
    ]
