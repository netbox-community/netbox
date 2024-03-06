from rest_framework import serializers

from extras.models import Dashboard

__all__ = (
    'DashboardSerializer',
)


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ('layout', 'config')
