import logging

from django.core.files.storage import storages
from django.db import IntegrityError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.api.serializers_.jobs import JobSerializer
from core.choices import ManagedFileRootPathChoices
from extras.models import Script, ScriptModule
from netbox.api.serializers import ValidatedModelSerializer
from utilities.datetime import local_now

logger = logging.getLogger(__name__)

__all__ = (
    'ScriptDetailSerializer',
    'ScriptInputSerializer',
    'ScriptModuleSerializer',
    'ScriptSerializer',
)


class ScriptModuleSerializer(ValidatedModelSerializer):
    file = serializers.FileField(write_only=True)
    file_path = serializers.CharField(read_only=True)

    class Meta:
        model = ScriptModule
        fields = ['id', 'display', 'file_path', 'file', 'created', 'last_updated']
        brief_fields = ('id', 'display')

    def validate(self, data):
        # ScriptModule.save() sets file_root; inject it here so full_clean() succeeds.
        # Pop 'file' before model instantiation — ScriptModule has no such field.
        file = data.pop('file', None)
        data['file_root'] = ManagedFileRootPathChoices.SCRIPTS
        data = super().validate(data)
        data.pop('file_root', None)
        if file is not None:
            data['file'] = file
        return data

    def create(self, validated_data):
        file = validated_data.pop('file')
        storage = storages.create_storage(storages.backends["scripts"])
        validated_data['file_path'] = storage.save(file.name, file)
        created = False
        try:
            instance = super().create(validated_data)
            created = True
            return instance
        except IntegrityError as e:
            if 'file_path' in str(e):
                raise serializers.ValidationError(
                    _("A script module with this file name already exists.")
                )
            raise
        finally:
            if not created and (file_path := validated_data.get('file_path')):
                try:
                    storage.delete(file_path)
                except Exception:
                    logger.warning(f"Failed to delete orphaned script file '{file_path}' from storage.")


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
        return {}

    @extend_schema_field(serializers.CharField())
    def get_display(self, obj):
        return f'{obj.name} ({obj.module})'

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_description(self, obj):
        if obj.python_class:
            return obj.python_class().description
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
        """
        Validates the specified schedule time for a script execution.
        """
        if value:
            if not self.context['script'].python_class.scheduling_enabled:
                raise serializers.ValidationError(_('Scheduling is not enabled for this script.'))
            if value < local_now():
                raise serializers.ValidationError(_('Scheduled time must be in the future.'))
        return value

    def validate_interval(self, value):
        """
        Validates the provided interval based on the script's scheduling configuration.
        """
        if value and not self.context['script'].python_class.scheduling_enabled:
            raise serializers.ValidationError(_('Scheduling is not enabled for this script.'))
        return value

    def validate(self, data):
        """
        Validates the given data and ensures the necessary fields are populated.
        """
        # Set the schedule_at time to now if only an interval is provided
        # while handling the case where schedule_at is null.
        if data.get('interval') and not data.get('schedule_at'):
            data['schedule_at'] = local_now()

        return super().validate(data)
