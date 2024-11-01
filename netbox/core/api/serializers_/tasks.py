from rest_framework import serializers

__all__ = (
    'BackgroundTaskSerializer',
    'BackgroundQueueSerializer',
)


class BackgroundTaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    description = serializers.CharField()
    origin = serializers.CharField()
    enqueued_at = serializers.CharField()
    started_at = serializers.CharField()
    ended_at = serializers.DictField()
    worker_name = serializers.DictField()
    position = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_finished = serializers.BooleanField()
    is_queued = serializers.BooleanField()
    is_failed = serializers.BooleanField()
    is_started = serializers.BooleanField()
    is_deferred = serializers.BooleanField()
    is_canceled = serializers.BooleanField()
    is_scheduled = serializers.BooleanField()
    is_stopped = serializers.BooleanField()

    def get_position(self, obj):
        return obj.get_position()

    def get_status(self, obj):
        return obj.get_status()


class BackgroundQueueSerializer(serializers.Serializer):
    name = serializers.CharField()
    jobs = serializers.IntegerField()
    oldest_job_timestamp = serializers.CharField()
    index = serializers.IntegerField()
    connection_kwargs = serializers.DictField()
    scheduler_pid = serializers.CharField()
    workers = serializers.IntegerField()
    finished_jobs = serializers.IntegerField()
    started_jobs = serializers.IntegerField()
    deferred_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    scheduled_jobs = serializers.IntegerField()
