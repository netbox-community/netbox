from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.api.serializers_.jobs import JobSerializer
from extras.models import Script
from netbox.api.serializers import ValidatedModelSerializer

__all__ = (
    'ScriptDetailSerializer',
    'ScriptInputSerializer',
    'ScriptSerializer',
)


class ScriptSerializer(ValidatedModelSerializer):
    description = serializers.SerializerMethodField(read_only=True)
    vars = serializers.SerializerMethodField(read_only=True)
    result = JobSerializer(nested=True, read_only=True)

    class Meta:
        model = Script
        fields = [
            'id', 'url', 'display_url', 'module', 'name', 'description', 'vars', 'result', 'display', 'is_executable',
        ]
        brief_fields = ('id', 'url', 'display', 'name', 'description')

    @extend_schema_field(serializers.JSONField(allow_null=True))
    def get_vars(self, obj):
        if obj.python_class:
            return {
                k: v.__class__.__name__ for k, v in obj.python_class()._get_vars().items()
            }
        else:
            return {}

    @extend_schema_field(serializers.CharField())
    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'

    @extend_schema_field(serializers.CharField())
    def get_description(self, obj):
        if obj.python_class:
            return obj.python_class().description
        else:
            return None


class ScriptDetailSerializer(ScriptSerializer):
    result = serializers.SerializerMethodField(read_only=True)

    @extend_schema_field(JobSerializer())
    def get_result(self, obj):
        job = obj.jobs.all().order_by('-created').first()
        context = {
            'request': self.context['request']
        }
        data = JobSerializer(job, context=context).data
        return data


class ScriptInputSerializer(serializers.Serializer):
    data = serializers.JSONField()
    commit = serializers.BooleanField()
    schedule_at = serializers.DateTimeField(required=False, allow_null=True)
    interval = serializers.IntegerField(required=False, allow_null=True)

    def validate_schedule_at(self, value):
        if value and not self.context['script'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this script."))
        return value

    def validate_interval(self, value):
        if value and not self.context['script'].scheduling_enabled:
            raise serializers.ValidationError(_("Scheduling is not enabled for this script."))
        return value
