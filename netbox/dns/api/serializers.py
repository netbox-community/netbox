from rest_framework import serializers

from ipam.api.serializers import IPAddressNestedSerializer
from dns.models import Zone, Record

#
# Zones
#


class ZoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Zone
        fields = ['id', 'name', 'ttl', 'soa_name', 'soa_contact', 'soa_serial', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum', 'extra_conf', 'description']


class ZoneNestedSerializer(ZoneSerializer):

    class Meta(ZoneSerializer.Meta):
        fields = ['id', 'name']


#
# Records
#


class RecordSerializer(serializers.ModelSerializer):

    zone = ZoneNestedSerializer()
    address = IPAddressNestedSerializer()

    class Meta:
        model = Record
        fields = ['id', 'name', 'record_type', 'priority', 'zone', 'address', 'value', 'description']


class RecordNestedSerializer(RecordSerializer):

    class Meta(RecordSerializer.Meta):
        fields = ['id', 'name', 'record_type', 'zone']
