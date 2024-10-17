import json
import logging
import sys
import uuid

from django.core.management.base import BaseCommand, CommandError

from extras.jobs import ScriptJob
from extras.scripts import get_module_and_script
from users.models import User
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
        # Params
        script = options['script']
        loglevel = options['loglevel']
        commit = options['commit']

        try:
            data = json.loads(options['data'])
        except TypeError:
            data = {}

        module_name, script_name = script.split('.', 1)
        module, script_obj = get_module_and_script(module_name, script_name)
        script = script_obj.python_class

        # Take user from command line if provided and exists, other
        if options['user']:
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                user = User.objects.filter(is_superuser=True).order_by('pk')[0]
        else:
            user = User.objects.filter(is_superuser=True).order_by('pk')[0]

        # Setup logging to Stdout
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] - %(message)s')
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
        if not form.is_valid():
            logger.error('Data is not valid:')
            for field, errors in form.errors.get_json_data().items():
                for error in errors:
                    logger.error(f'\t{field}: {error.get("message")}')
            raise CommandError()

        # Execute the script.
        job = ScriptJob.enqueue(
            instance=script_obj,
            user=user,
            immediate=True,
            data=data,
            request=NetBoxFakeRequest({
                'META': {},
                'POST': data,
                'GET': {},
                'FILES': {},
                'user': user,
                'path': '',
                'id': uuid.uuid4()
            }),
            commit=commit,
        )

        logger.info(f"Script completed in {job.duration}")
