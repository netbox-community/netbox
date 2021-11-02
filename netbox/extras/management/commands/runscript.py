import json
import logging
import sys
import traceback
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from extras.api.serializers import ScriptOutputSerializer
from extras.choices import JobResultStatusChoices
from extras.context_managers import change_logging
from extras.models import JobResult
from extras.scripts import get_script
from utilities.exceptions import AbortTransaction
from utilities.utils import NetBoxFakeRequest


class Command(BaseCommand):
    help = "Run a script in Netbox"

    def add_arguments(self, parser):
        parser.add_argument(
            '--loglevel',
            help="Logging Level (default: info)",
            dest='loglevel',
            default='info',
            choices=['debug', 'info', 'warning', 'error', 'critical'])
        parser.add_argument('--script', help="Script to run", required=True)
        parser.add_argument('--commit', help="Commit this script to database", action='store_true')
        parser.add_argument('--user', help="User script is running as")
        parser.add_argument('data', help="Data as a string encapsulated JSON blob")

    def handle(self, *args, **options):
        def _run_script():
            """
            Core script execution task. We capture this within a subfunction to allow for conditionally wrapping it with
            the change_logging context manager (which is bypassed if commit == False).
            """
            try:
                with transaction.atomic():
                    script.output = script.run(data=data, commit=commit)
                    job_result.set_status(JobResultStatusChoices.STATUS_COMPLETED)

                    if not commit:
                        raise AbortTransaction()

            except AbortTransaction:
                script.log_info("Database changes have been reverted automatically.")

            except Exception as e:
                stacktrace = traceback.format_exc()
                script.log_failure(
                    f"An exception occurred: `{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
                )
                script.log_info("Database changes have been reverted due to error.")
                logger.error(f"Exception raised during script execution: {e}")
                job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)

            finally:
                job_result.data = ScriptOutputSerializer(script).data
                job_result.save()

            logger.info(f"Script completed in {job_result.duration}")

        # Params
        script = options['script']
        loglevel = options['loglevel']
        commit = options['commit']
        data = json.loads(options['data']) if options['data'] is not None else None

        module, name = script.split('.', 1)

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

        logger = logging.getLogger(f"netbox.scripts.{module}.{name}")
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

        # Get the script
        script = get_script(module, name)()
        # Parse the parameters
        form = script.as_form(data, None)

        script_content_type = ContentType.objects.get(app_label='extras', model='script')

        # Delete any previous terminal state results
        JobResult.objects.filter(
            obj_type=script_content_type,
            name=script.full_name,
            status__in=JobResultStatusChoices.TERMINAL_STATE_CHOICES
        ).delete()

        # Create the job result
        job_result = JobResult.objects.create(
            name=script.full_name,
            obj_type=script_content_type,
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
            'id': job_result.job_id
        })

        if form.is_valid():
            job_result.status = JobResultStatusChoices.STATUS_RUNNING
            job_result.save()

            logger.info(f"Running script (commit={commit})")
            script.request = request

            # Execute the script. If commit is True, wrap it with the change_logging context manager to ensure we process
            # change logging, webhooks, etc.
            with change_logging(request):
                _run_script()
        else:
            logger.error('Data is not valid:')
            for field, errors in form.errors.get_json_data().items():
                for error in errors:
                    logger.error(f'\t{field}: {error.get("message")}')
            job_result.status = JobResultStatusChoices.STATUS_ERRORED
            job_result.save()
