from rest_framework import serializers

__all__ = (
    'BackgroundQueueSerializer',
)


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
