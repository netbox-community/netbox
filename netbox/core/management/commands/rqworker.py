import logging

from django_rq.management.commands.rqworker import Command as _Command

from netbox.registry import registry


DEFAULT_QUEUES = ('high', 'default', 'low')

logger = logging.getLogger('netbox.rqworker')


class Command(_Command):
    """
    Subclass django_rq's built-in rqworker to listen on all configured queues if none are specified (instead
    of only the 'default' queue).
    """
    def handle(self, *args, **options):
        # Setup system jobs.
        for job, kwargs in registry['system_jobs'].items():
            try:
                interval = kwargs['interval']
            except KeyError:
                raise TypeError("System job must specify an interval (in minutes).")
            logger.debug(f"Scheduling system job {job.name} (interval={interval})")
            job.enqueue_once(**kwargs)

        # Run the worker with scheduler functionality
        options['with_scheduler'] = True

        # If no queues have been specified on the command line, listen on all configured queues.
        if len(args) < 1:
            queues = ', '.join(DEFAULT_QUEUES)
            logger.warning(
                f"No queues have been specified. This process will service the following queues by default: {queues}"
            )
            args = DEFAULT_QUEUES

        super().handle(*args, **options)
