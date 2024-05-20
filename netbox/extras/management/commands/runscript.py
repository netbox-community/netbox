import json
import logging
import sys
import traceback
import uuid

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.choices import JobStatusChoices
from core.models import Job
from extras.context_managers import event_tracking
from extras.scripts import get_module_and_script
from extras.signals import clear_events
from utilities.exceptions import AbortTransaction
from utilities.request import NetBoxFakeRequest


class Command(BaseCommand):
    help = "Run a script in NetBox"

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            help="Logging Level (default: info)",
            dest='loglevel',
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'])
        parser.add_argument('--commit', help="Commit this script to database", action='store_true')
        parser.add_argument('--user', help="User script is running as")
        parser.add_argument('--data', help="Data as a string encapsulated JSON blob")
        parser.add_argument('script', help="Script to run")

    def handle(self, *args, **options):

        def _run_script():
            """
            Core script execution task. We capture this within a subfunction to allow for conditionally wrapping it with
            the event_tracking context manager (which is bypassed if commit == False).
            """
            try:
                try:
                    with transaction.atomic():
                        script.output = script.run(data=data, commit=commit)
                        if not commit:
                            raise AbortTransaction()
                except AbortTransaction:
                    script.log_info("Database changes have been reverted automatically.")
                    clear_events.send(request)
                job.data = script.get_job_data()
                job.terminate()
            except Exception as e:
                stacktrace = traceback.format_exc()
                script.log_failure(
                    f"An exception occurred: `{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
                )
                script.log_info("Database changes have been reverted due to error.")
                logger.error(f"Exception raised during script execution: {e}")
                clear_events.send(request)
                job.data = script.get_job_data()
                job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))

            # Print any test method results
            for test_name, attrs in job.data['tests'].items():
                self.stdout.write(
                    "\t{}: {} success, {} info, {} warning, {} failure".format(
                        test_name, attrs['success'], attrs['info'], attrs['warning'], attrs['failure']
                    )
                )

            logger.info(f"Script completed in {job.duration}")

        User = get_user_model()

        # Params
        script = options['script']
        loglevel = options['loglevel']
        commit = options['commit']

        try:
            data = json.loads(options['data'])
        except TypeError:
            data = {}

        module_name, script_name = script.split('.', 1)
        module, script = get_module_and_script(module_name, script_name)
        script = script.python_class

        # Take user from command line if provided and exists, other
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                user = User.objects.filter(is_superuser=True).order_by('pk')[0]
        else:
            user = User.objects.filter(is_superuser=True).order_by('pk')[0]

        # Setup logging to Stdout
        formatter = logging.Formatter(f'[%(asctime)s][%(levelname)s] - %(message)s')
        stdouthandler = logging.StreamHandler(sys.stdout)
        stdouthandler.setLevel(logging.DEBUG)
        stdouthandler.setFormatter(formatter)

        logger = logging.getLogger(f"netbox.scripts.{script.full_name}")
        logger.addHandler(stdouthandler)

        try:
            logger.setLevel({
                'critical': logging.CRITICAL,
                'debug': logging.DEBUG,
                'error': logging.ERROR,
                'fatal': logging.FATAL,
                'info': logging.INFO,
                'warning': logging.WARNING,
            }[loglevel])
        except KeyError:
            raise CommandError(f"Invalid log level: {loglevel}")

        # Initialize the script form
        script = script()
        form = script.as_form(data, None)

        # Create the job
        job = Job.objects.create(
            object=module,
            name=script.class_name,
            user=User.objects.filter(is_superuser=True).order_by('pk')[0],
            job_id=uuid.uuid4()
        )

        request = NetBoxFakeRequest({
            'META': {},
            'POST': data,
            'GET': {},
            'FILES': {},
            'user': user,
            'path': '',
            'id': job.job_id
        })

        if form.is_valid():
            job.status = JobStatusChoices.STATUS_RUNNING
            job.save()

            logger.info(f"Running script (commit={commit})")
            script.request = request

            # Execute the script. If commit is True, wrap it with the event_tracking context manager to ensure we process
            # change logging, webhooks, etc.
            with event_tracking(request):
                _run_script()
        else:
            logger.error('Data is not valid:')
            for field, errors in form.errors.get_json_data().items():
                for error in errors:
                    logger.error(f'\t{field}: {error.get("message")}')
            job.status = JobStatusChoices.STATUS_ERRORED
            job.save()
