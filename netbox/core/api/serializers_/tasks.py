from rest_framework import serializers
from rest_framework.reverse import reverse

__all__ = (
    'BackgroundTaskSerializer',
    'BackgroundQueueSerializer',
    'BackgroundWorkerSerializer',
)


class BackgroundTaskSerializer(serializers.Serializer):
    id = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:rqtask-detail',
        lookup_field='id',
        lookup_url_kwarg='pk'
    )
    description = serializers.CharField()
    origin = serializers.CharField()
    func_name = serializers.CharField()
    args = serializers.ListField(child=serializers.CharField())
    kwargs = serializers.DictField()
    result = serializers.CharField()
    timeout = serializers.IntegerField()
    result_ttl = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    enqueued_at = serializers.DateTimeField()
    started_at = serializers.DateTimeField()
    ended_at = serializers.DateTimeField()
    worker_name = serializers.CharField()
    position = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    meta = serializers.DictField()
    last_heartbeat = serializers.CharField()

    is_finished = serializers.BooleanField()
    is_queued = serializers.BooleanField()
    is_failed = serializers.BooleanField()
    is_started = serializers.BooleanField()
    is_deferred = serializers.BooleanField()
    is_canceled = serializers.BooleanField()
    is_scheduled = serializers.BooleanField()
    is_stopped = serializers.BooleanField()

    def get_position(self, obj) -> int:
        return obj.get_position()

    def get_status(self, obj) -> str:
        return obj.get_status()


class BackgroundQueueSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.SerializerMethodField()
    jobs = serializers.IntegerField()
    oldest_job_timestamp = serializers.CharField()
    index = serializers.IntegerField()
    scheduler_pid = serializers.CharField()
    workers = serializers.IntegerField()
    finished_jobs = serializers.IntegerField()
    started_jobs = serializers.IntegerField()
    deferred_jobs = serializers.IntegerField()
    failed_jobs = serializers.IntegerField()
    scheduled_jobs = serializers.IntegerField()

    def get_url(self, obj):
        return reverse('core-api:rqqueue-detail', args=[obj['name']], request=self.context.get("request"))


class BackgroundWorkerSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.HyperlinkedIdentityField(
        view_name='core-api:rqworker-detail',
        lookup_field='name'
    )
    state = serializers.SerializerMethodField()
    birth_date = serializers.DateTimeField()
    queue_names = serializers.ListField(
        child=serializers.CharField()
    )
    pid = serializers.CharField()
    successful_job_count = serializers.IntegerField()
    failed_job_count = serializers.IntegerField()
    total_working_time = serializers.IntegerField()

    def get_state(self, obj):
        return obj.get_state()
