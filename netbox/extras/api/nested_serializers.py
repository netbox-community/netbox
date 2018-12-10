from rest_framework import serializers

from extras.models import ReportResult

__all__ = [
    'NestedReportResultSerializer',
]


#
# Reports
#

class NestedReportResultSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='extras-api:report-detail',
        lookup_field='report',
        lookup_url_kwarg='pk'
    )

    class Meta:
        model = ReportResult
        fields = ['url', 'created', 'user', 'failed']
