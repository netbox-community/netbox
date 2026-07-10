import logging

from django.core.files.storage import storages
from django.db import IntegrityError, router, transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from core.api.serializers_.jobs import JobSerializer
from core.choices import JobNotificationChoices, ManagedFileRootPathChoices
from extras.models import Script, ScriptModule
from extras.utils import validate_script_content
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

        if self.instance is None:
            # Reject duplicates before writing to storage so a failed upload can't touch the existing file
            if file is not None and ScriptModule.objects.filter(
                file_root=ManagedFileRootPathChoices.SCRIPTS, file_path=file.name
            ).exists():
                raise serializers.ValidationError(_("A script module with this file name already exists."))
        elif file is None:
            # Replacing a module's content requires a file upload, even for a partial update
            raise serializers.ValidationError({'file': _("This field is required.")})
        elif file.name != self.instance.file_path:
            raise serializers.ValidationError({
                'file': _(
                    "The uploaded file name must match the existing file path ({path})."
                ).format(path=self.instance.file_path)
            })

        data = super().validate(data)
        data.pop('file_root', None)
        if file is not None:
            # Validate that the uploaded script can be loaded as a Python module
            content = file.read()
            file.seek(0)
            try:
                validate_script_content(content, file.name)
            except Exception as e:
                raise serializers.ValidationError(
                    _("Error loading script: {error}").format(error=e)
                )
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
            # Don't delete a path another ScriptModule still references (e.g. a concurrent upload won the race)
            file_path = validated_data.get('file_path')
            if not created and file_path and not ScriptModule.objects.filter(
                file_root=ManagedFileRootPathChoices.SCRIPTS, file_path=file_path
            ).exists():
                try:
                    storage.delete(file_path)
                except Exception:
                    logger.warning(f"Failed to delete orphaned script file '{file_path}' from storage.")

    def update(self, instance, validated_data):
        file = validated_data.pop('file')
        storage = storages.create_storage(storages.backends["scripts"])

        # Overwrite the existing file in place, keeping file_path stable
        file.seek(0)
        saved_path = storage.save(instance.file_path, file)
        if saved_path != instance.file_path:
            # The backend saved under an alternate name instead of overwriting; drop the orphan and reject
            try:
                storage.delete(saved_path)
            except Exception:
                logger.warning(f"Failed to delete orphaned script file '{saved_path}' from storage.")
            raise serializers.ValidationError({
                'file': _(
                    "The scripts storage backend did not overwrite the existing file. Ensure the "
                    "backend is configured to allow overwrites."
                )
            })

        # Discard any cached class discovery so save() re-syncs from the new content
        instance.__dict__.pop('module_scripts', None)
        instance.last_updated = local_now()
        # Keep Script row sync all-or-nothing; the storage write above cannot join the transaction
        with transaction.atomic(using=router.db_for_write(ScriptModule)):
            instance.save()

        return instance


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
    notifications = serializers.ChoiceField(
        choices=JobNotificationChoices,
        required=False,
        default=JobNotificationChoices.NOTIFICATION_ALWAYS,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default to script's Meta.notifications_default if set
        script = self.context.get('script')
        if script and script.python_class:
            self.fields['notifications'].default = script.python_class.notifications_default

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
