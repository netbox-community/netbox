from rest_framework import generics
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response

from ipam.models import IPAddress
from dns.models import Zone, Record, export_bind_forward, export_bind_reverse
from dns import filters

from . import serializers

#
# Zones
#


class ZoneListView(generics.ListAPIView):
    """
    List all zones
    """
    queryset = Zone.objects.all()
    serializer_class = serializers.ZoneSerializer
    filter_class = filters.ZoneFilter


class ZoneDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single zone
    """
    queryset = Zone.objects.all()
    serializer_class = serializers.ZoneSerializer


#
# Records
#


class RecordListView(generics.ListAPIView):
    """
    List all records
    """
    queryset = Record.objects.all()
    serializer_class = serializers.RecordSerializer


class RecordDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single record
    """
    queryset = Record.objects.all()
    serializer_class = serializers.RecordSerializer


#
# BIND Exports
#


@api_view(['GET'])
def bind_forward(request):
    """
    Full export of forward zones in BIND format
    """
    zones_list = export_bind_forward()
    return Response(zones_list)


@api_view(['GET'])
def bind_reverse(request):
    """
    Full export of reverse zones in BIND format
    """
    zones_list = export_bind_reverse()
    return Response(zones_list)
