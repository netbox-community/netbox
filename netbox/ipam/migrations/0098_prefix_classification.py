from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('ipam', '0097_merge_ipaddress_host_index_and_multi_protocol_services'),
    ]

    operations = [
        migrations.AddField(
            model_name='prefix',
            name='classification',
            field=models.GeneratedField(
                db_persist=True,
                expression=models.Case(
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '192.0.0.9/32'),
                            ('prefix__net_contained_or_equal', '192.0.0.10/32'),
                            ('prefix__net_contained_or_equal', '64:ff9b::/96'),
                            ('prefix__net_contained_or_equal', '2001:1::1/128'),
                            ('prefix__net_contained_or_equal', '2001:1::2/127'),
                            ('prefix__net_contained_or_equal', '2001:3::/32'),
                            ('prefix__net_contained_or_equal', '2001:4:112::/48'),
                            ('prefix__net_contained_or_equal', '2001:20::/27'),
                            _connector='OR',
                        ),
                        then=models.Value('public'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '10.0.0.0/8'),
                            ('prefix__net_contained_or_equal', '172.16.0.0/12'),
                            ('prefix__net_contained_or_equal', '192.168.0.0/16'),
                            ('prefix__net_contained_or_equal', 'fc00::/7'),
                            _connector='OR',
                        ),
                        then=models.Value('private'),
                    ),
                    models.When(
                        models.Q(('prefix__net_contained_or_equal', '100.64.0.0/10'), _connector='OR'),
                        then=models.Value('shared'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '127.0.0.0/8'),
                            ('prefix__net_contained_or_equal', '::1/128'),
                            _connector='OR',
                        ),
                        then=models.Value('loopback'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '169.254.0.0/16'),
                            ('prefix__net_contained_or_equal', 'fe80::/10'),
                            _connector='OR',
                        ),
                        then=models.Value('link-local'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '192.0.2.0/24'),
                            ('prefix__net_contained_or_equal', '198.51.100.0/24'),
                            ('prefix__net_contained_or_equal', '203.0.113.0/24'),
                            ('prefix__net_contained_or_equal', '2001:db8::/32'),
                            ('prefix__net_contained_or_equal', '3fff::/20'),
                            _connector='OR',
                        ),
                        then=models.Value('documentation'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '224.0.0.0/4'),
                            ('prefix__net_contained_or_equal', 'ff00::/8'),
                            _connector='OR',
                        ),
                        then=models.Value('multicast'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '198.18.0.0/15'),
                            ('prefix__net_contained_or_equal', '2001:2::/48'),
                            _connector='OR',
                        ),
                        then=models.Value('benchmarking'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contains', '192.0.0.9/32'),
                            ('prefix__net_contains', '192.0.0.10/32'),
                            ('prefix__net_contains', '64:ff9b::/96'),
                            ('prefix__net_contains', '2001:1::1/128'),
                            ('prefix__net_contains', '2001:1::2/127'),
                            ('prefix__net_contains', '2001:3::/32'),
                            ('prefix__net_contains', '2001:4:112::/48'),
                            ('prefix__net_contains', '2001:20::/27'),
                            ('prefix__net_contains', '10.0.0.0/8'),
                            ('prefix__net_contains', '172.16.0.0/12'),
                            ('prefix__net_contains', '192.168.0.0/16'),
                            ('prefix__net_contains', 'fc00::/7'),
                            ('prefix__net_contains', '100.64.0.0/10'),
                            ('prefix__net_contains', '127.0.0.0/8'),
                            ('prefix__net_contains', '::1/128'),
                            ('prefix__net_contains', '169.254.0.0/16'),
                            ('prefix__net_contains', 'fe80::/10'),
                            ('prefix__net_contains', '192.0.2.0/24'),
                            ('prefix__net_contains', '198.51.100.0/24'),
                            ('prefix__net_contains', '203.0.113.0/24'),
                            ('prefix__net_contains', '2001:db8::/32'),
                            ('prefix__net_contains', '3fff::/20'),
                            ('prefix__net_contains', '224.0.0.0/4'),
                            ('prefix__net_contains', 'ff00::/8'),
                            ('prefix__net_contains', '198.18.0.0/15'),
                            ('prefix__net_contains', '2001:2::/48'),
                            _connector='OR',
                        ),
                        then=models.Value('mixed'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contained_or_equal', '0.0.0.0/8'),
                            ('prefix__net_contained_or_equal', '192.0.0.0/24'),
                            ('prefix__net_contained_or_equal', '192.88.99.0/24'),
                            ('prefix__net_contained_or_equal', '240.0.0.0/4'),
                            ('prefix__net_contained_or_equal', '::/3'),
                            ('prefix__net_contained_or_equal', '2001::/23'),
                            ('prefix__net_contained_or_equal', '2002::/16'),
                            ('prefix__net_contained_or_equal', '4000::/2'),
                            ('prefix__net_contained_or_equal', '8000::/2'),
                            ('prefix__net_contained_or_equal', 'c000::/3'),
                            ('prefix__net_contained_or_equal', 'e000::/4'),
                            ('prefix__net_contained_or_equal', 'f000::/5'),
                            ('prefix__net_contained_or_equal', 'f800::/6'),
                            ('prefix__net_contained_or_equal', 'fe00::/9'),
                            ('prefix__net_contained_or_equal', 'fec0::/10'),
                            _connector='OR',
                        ),
                        then=models.Value('special'),
                    ),
                    models.When(
                        models.Q(
                            ('prefix__net_contains', '0.0.0.0/8'),
                            ('prefix__net_contains', '192.0.0.0/24'),
                            ('prefix__net_contains', '192.88.99.0/24'),
                            ('prefix__net_contains', '240.0.0.0/4'),
                            ('prefix__net_contains', '::/3'),
                            ('prefix__net_contains', '2001::/23'),
                            ('prefix__net_contains', '2002::/16'),
                            ('prefix__net_contains', '4000::/2'),
                            ('prefix__net_contains', '8000::/2'),
                            ('prefix__net_contains', 'c000::/3'),
                            ('prefix__net_contains', 'e000::/4'),
                            ('prefix__net_contains', 'f000::/5'),
                            ('prefix__net_contains', 'f800::/6'),
                            ('prefix__net_contains', 'fe00::/9'),
                            ('prefix__net_contains', 'fec0::/10'),
                            _connector='OR',
                        ),
                        then=models.Value('mixed'),
                    ),
                    default=models.Value('public'),
                    output_field=models.CharField(max_length=50),
                ),
                output_field=models.CharField(max_length=50),
            ),
        ),
    ]
