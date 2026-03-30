import os

from django.core.files.storage import storages
from django.db import IntegrityError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.api.serializers_.data import DataFileSerializer, DataSourceSerializer
from core.api.serializers_.jobs import JobSerializer
from core.choices import ManagedFileRootPathChoices
from extras.models import Script, ScriptModule
from netbox.api.serializers import ValidatedModelSerializer
from utilities.datetime import local_now

__all__ = (
    'ScriptDetailSerializer',
    'ScriptInputSerializer',
    'ScriptModuleSerializer',
    'ScriptSerializer',
)


class ScriptModuleSerializer(ValidatedModelSerializer):
    url = None
    data_source = DataSourceSerializer(nested=True, required=False, allow_null=True)
    data_file = DataFileSerializer(nested=True, required=False, allow_null=True)
    upload_file = serializers.FileField(write_only=True, required=False, allow_null=True)
    file_path = serializers.CharField(read_only=True)

    class Meta:
        model = ScriptModule
        fields = [
            'id', 'display', 'file_path', 'upload_file',
            'data_source', 'data_file', 'auto_sync_enabled',
            'created', 'last_updated',
        ]
        brief_fields = ('id', 'display')

    def validate(self, data):
        upload_file = data.pop('upload_file', None)

        # For multipart requests, nested serializer fields (data_source, data_file) are
        # silently dropped by DRF's HTML parser, so also check initial_data for raw values.
        # These checks must run before super().validate() calls full_clean(), which would
        # otherwise surface confusing unique-constraint errors for empty file_path values.
        has_data_file = data.get('data_file') or self.initial_data.get('data_file')
        has_data_source = data.get('data_source') or self.initial_data.get('data_source')

        if upload_file and has_data_file:
            raise serializers.ValidationError(
                _("Cannot upload a file and sync from an existing file.")
            )
        if upload_file and has_data_source:
            raise serializers.ValidationError(
                _("Cannot upload a file and sync from a data source.")
            )
        if has_data_source and not has_data_file:
            raise serializers.ValidationError(
                _("A data file must be specified when syncing from a data source.")
            )
        if self.instance is None and not upload_file and not has_data_file:
            raise serializers.ValidationError(
                _("Must upload a file or select a data file to sync.")
            )

        # ScriptModule.save() sets file_root; inject it here so full_clean() succeeds
        data['file_root'] = ManagedFileRootPathChoices.SCRIPTS
        data = super().validate(data)
        data.pop('file_root', None)
        if upload_file is not None:
            data['upload_file'] = upload_file

        return data

    def _save_upload(self, upload_file, validated_data):
        storage = storages.create_storage(storages.backends["scripts"])
        validated_data['file_path'] = storage.save(upload_file.name, upload_file)

    def _sync_data_file(self, data_file, validated_data):
        """
        Pre-populate file_path/data_path and write the file to disk before create(),
        so that save() → sync_classes() fires once with the correct file_path — matching
        the UI path where full_clean() sets these fields on the actual instance before save().
        """
        file_path = os.path.basename(data_file.path)
        validated_data['data_path'] = data_file.path
        validated_data['file_path'] = file_path
        validated_data['data_synced'] = timezone.now()
        storage = storages.create_storage(storages.backends["scripts"])
        with storage.open(file_path, 'wb+') as f:
            f.write(data_file.data)

    def create(self, validated_data):
        upload_file = validated_data.pop('upload_file', None)
        if upload_file:
            self._save_upload(upload_file, validated_data)
        elif data_file := validated_data.get('data_file'):
            self._sync_data_file(data_file, validated_data)
        try:
            return super().create(validated_data)
        except IntegrityError:
            # ManagedFile has a single unique constraint: (file_root, file_path), so an
            # IntegrityError here always means a duplicate file name regardless of which
            # path (upload or data_file sync) set validated_data['file_path'].
            # Clean up the file written to disk before the failed DB insert.
            if file_path := validated_data.get('file_path'):
                storage = storages.create_storage(storages.backends["scripts"])
                storage.delete(file_path)
            raise serializers.ValidationError(
                _("A script module with this file name already exists.")
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
