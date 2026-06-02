from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from django.db import DEFAULT_DB_ALIAS
from django.test import TestCase

from extras.jobs import ScriptJob
from utilities.exceptions import AbortScript


def _make_runner(**job_attrs):
    """
    Build a ScriptJob without going through ``__init__``.

    ``JobRunner.__init__`` attaches a ``JobLogHandler`` to a module-level
    singleton logger; instantiating one per test would accumulate handlers.
    """
    runner = ScriptJob.__new__(ScriptJob)
    runner.job = MagicMock(**job_attrs)
    runner.logger = MagicMock()
    return runner


class DummyScript:
    """A minimal stand-in for a Script implementation."""

    full_name = 'tests.DummyScript'

    def __init__(self, run_result=None, run_exception=None, failed=False):
        self._run_result = run_result
        self._run_exception = run_exception
        self.failed = failed
        self.output = None
        self.request = None
        self.run = MagicMock(side_effect=self._run_impl)
        self.log_info = MagicMock()
        self.log_failure = MagicMock()
        self.get_job_data = MagicMock(return_value={'status': 'done'})

    def _run_impl(self, data, commit):
        if self._run_exception is not None:
            raise self._run_exception
        return self._run_result


class RunScriptTestCase(TestCase):
    def test_run_script_success_commit_true_sets_output_and_job_data(self):
        runner = _make_runner()
        script = DummyScript(run_result='hello')

        runner.run_script(script, request=None, data={'k': 'v'}, commit=True)

        self.assertEqual(script.output, 'hello')
        script.run.assert_called_once_with({'k': 'v'}, True)
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_commit_false_rolls_back_without_raising(self):
        runner = _make_runner()
        script = DummyScript(run_result='hello')

        runner.run_script(script, request=None, data={}, commit=False)

        script.run.assert_called_once_with({}, False)
        # Rollback path: log_info() is called (with the translated revert message);
        # job.data is still populated. Don't assert exact wording.
        script.log_info.assert_called_once()
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_commit_false_logs_warning_when_script_failed(self):
        runner = _make_runner()
        script = DummyScript(run_result='hello', failed=True)

        with patch('extras.jobs.logging.getLogger') as get_logger:
            logger = get_logger.return_value
            runner.run_script(script, request=None, data={}, commit=False)

        logger.warning.assert_any_call('Script failed')

    def test_run_script_abort_script_logs_failure_and_reraises(self):
        # Non-report scripts call `script.log_failure(msg)` positionally; report-style
        # scripts use `log_failure(message=msg)`. See `test_run_script_abort_script_uses_report_log_failure_signature`.
        runner = _make_runner()
        script = DummyScript(run_exception=AbortScript('nope'))

        with self.assertRaises(AbortScript):
            runner.run_script(script, request=None, data={}, commit=True)

        # Outcome assertions: AbortScript re-raised, failure logged on the script,
        # rollback path traversed (log_info called), job.data populated.
        script.log_failure.assert_called_once()
        # Non-report path uses the positional signature; verify both that there is
        # a positional arg and no `message=` kwarg.
        self.assertTrue(script.log_failure.call_args.args)
        self.assertFalse(script.log_failure.call_args.kwargs)
        script.log_info.assert_called_once()
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_abort_script_uses_report_log_failure_signature(self):
        runner = _make_runner()
        script = DummyScript(run_exception=AbortScript('reportfail'))

        with (
            patch('extras.jobs.is_report', return_value=True),
            self.assertRaises(AbortScript),
        ):
            runner.run_script(script, request=None, data={}, commit=True)

        # For reports, log_failure is called with the keyword-form signature.
        script.log_failure.assert_called_once()
        self.assertIn('message', script.log_failure.call_args.kwargs)

    def test_run_script_general_exception_logs_traceback_and_reraises(self):
        runner = _make_runner()
        script = DummyScript(run_exception=RuntimeError('boom'))

        with self.assertRaisesMessage(RuntimeError, 'boom'):
            runner.run_script(script, request=None, data={}, commit=True)

        script.log_failure.assert_called_once()
        # The failure message wraps a traceback; assert on the structural marker
        # (Traceback header) rather than translated copy.
        message = script.log_failure.call_args.kwargs['message']
        self.assertIn('Traceback', message)
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_sends_clear_events_when_request_is_present_and_error_occurs(self):
        runner = _make_runner()
        script = DummyScript(run_exception=RuntimeError('boom'))
        request = MagicMock()

        with patch('extras.jobs.clear_events.send') as send:
            with self.assertRaises(RuntimeError):
                runner.run_script(script, request=request, data={}, commit=True)

        send.assert_called_once_with(request)

    def test_run_script_default_db_uses_single_atomic(self):
        # Symmetric with test_run_script_enters_secondary_atomic_when_changelog_db_differs:
        # when the changelog DB is the default, only a single atomic() block is opened.
        runner = _make_runner()
        script = DummyScript(run_result='ok')
        atomic_calls = []

        @contextmanager
        def fake_atomic(using):
            atomic_calls.append(using)
            yield

        with (
            patch('extras.jobs.router.db_for_write', return_value=DEFAULT_DB_ALIAS),
            patch('extras.jobs.transaction.atomic', side_effect=fake_atomic),
        ):
            runner.run_script(script, request=None, data={}, commit=True)

        self.assertEqual(atomic_calls, [DEFAULT_DB_ALIAS])
        script.run.assert_called_once_with({}, True)
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_enters_secondary_atomic_when_changelog_db_differs(self):
        # Verifies that the code enters two nested atomic() context managers when
        # the changelog DB differs from the default. Does not exercise real rollback
        # semantics (transaction.atomic is patched).
        runner = _make_runner()
        script = DummyScript(run_result='ok')

        atomic_calls = []

        @contextmanager
        def fake_atomic(using):
            atomic_calls.append(using)
            yield

        with (
            patch('extras.jobs.router.db_for_write', return_value='changelog_db'),
            patch('extras.jobs.transaction.atomic', side_effect=fake_atomic),
        ):
            runner.run_script(script, request=None, data={}, commit=True)

        self.assertEqual(atomic_calls, [DEFAULT_DB_ALIAS, 'changelog_db'])
        script.run.assert_called_once_with({}, True)
        self.assertEqual(runner.job.data, {'status': 'done'})

    def test_run_script_enters_secondary_atomic_when_commit_false(self):
        # Mirror of the previous test for the commit=False branch on the secondary
        # DB path. Verifies both atomic blocks are entered; does not exercise true
        # rollback semantics (transaction.atomic is patched).
        runner = _make_runner()
        script = DummyScript(run_result='ok')
        atomic_calls = []

        @contextmanager
        def fake_atomic(using):
            atomic_calls.append(using)
            yield

        with (
            patch('extras.jobs.router.db_for_write', return_value='changelog_db'),
            patch('extras.jobs.transaction.atomic', side_effect=fake_atomic),
        ):
            runner.run_script(script, request=None, data={}, commit=False)

        self.assertEqual(atomic_calls, [DEFAULT_DB_ALIAS, 'changelog_db'])
        script.run.assert_called_once_with({}, False)
        script.log_info.assert_called_once()


class ScriptJobRunTestCase(TestCase):
    @staticmethod
    def _runner():
        return _make_runner(object_id=1)

    @staticmethod
    def _script_model(script_instance):
        return SimpleNamespace(pk=1, python_class=MagicMock(return_value=script_instance))

    def test_run_loads_script_model_and_instantiates_python_class(self):
        runner = self._runner()
        script_instance = DummyScript()
        script_model = self._script_model(script_instance)

        with (
            patch('extras.jobs.ScriptModel.objects.get', return_value=script_model) as get_script_model,
            patch.object(ScriptJob, 'run_script') as run_script,
            patch.dict('netbox.registry.registry', {'request_processors': []}, clear=False),
        ):
            runner.run(data={'k': 'v'}, commit=True)

        get_script_model.assert_called_once_with(pk=1)
        script_model.python_class.assert_called_once_with()
        run_script.assert_called_once()
        args, _ = run_script.call_args
        self.assertIs(args[0], script_instance)
        self.assertEqual(args[2], {'k': 'v'})  # data
        self.assertIs(args[3], True)  # commit

    def test_run_merges_request_files_into_data(self):
        runner = self._runner()
        script_instance = DummyScript()
        script_model = self._script_model(script_instance)
        request = MagicMock(FILES={'upload': 'fileobj'}, id='req-1')
        data = {'k': 'v'}

        with (
            patch('extras.jobs.ScriptModel.objects.get', return_value=script_model),
            patch.object(ScriptJob, 'run_script') as run_script,
            patch.dict('netbox.registry.registry', {'request_processors': []}, clear=False),
        ):
            runner.run(data=data, request=request, commit=True)

        passed_data = run_script.call_args.args[2]
        self.assertEqual(passed_data['k'], 'v')
        self.assertEqual(passed_data['upload'], 'fileobj')

    def test_run_sets_script_request_when_request_is_present(self):
        runner = self._runner()
        script_instance = DummyScript()
        script_model = self._script_model(script_instance)
        request = MagicMock(FILES={}, id='req-1')

        with (
            patch('extras.jobs.ScriptModel.objects.get', return_value=script_model),
            patch.object(ScriptJob, 'run_script'),
            patch.dict('netbox.registry.registry', {'request_processors': []}, clear=False),
        ):
            runner.run(data={}, request=request, commit=True)

        self.assertIs(script_instance.request, request)

    def _processor_factories(self, entered):
        def ctx_a(request):
            @contextmanager
            def _ctx():
                entered.append('proc_a')
                yield

            return _ctx()

        def ctx_event(request):
            @contextmanager
            def _ctx():
                entered.append('event_tracking')
                yield

            return _ctx()

        return ctx_a, ctx_event

    def test_run_uses_request_processors_when_commit_true(self):
        runner = self._runner()
        script_instance = DummyScript()
        script_model = self._script_model(script_instance)
        entered = []
        ctx_a, ctx_event = self._processor_factories(entered)

        with (
            patch('extras.jobs.ScriptModel.objects.get', return_value=script_model),
            patch.object(ScriptJob, 'run_script'),
            patch('extras.jobs.event_tracking', new=ctx_event),
            patch.dict(
                'netbox.registry.registry',
                {'request_processors': [ctx_a, ctx_event]},
                clear=False,
            ),
        ):
            runner.run(data={}, commit=True)

        self.assertEqual(entered, ['proc_a', 'event_tracking'])

    def test_run_skips_event_tracking_when_commit_false(self):
        runner = self._runner()
        script_instance = DummyScript()
        script_model = self._script_model(script_instance)
        entered = []
        ctx_a, ctx_event = self._processor_factories(entered)

        with (
            patch('extras.jobs.ScriptModel.objects.get', return_value=script_model),
            patch.object(ScriptJob, 'run_script'),
            patch('extras.jobs.event_tracking', new=ctx_event),
            patch.dict(
                'netbox.registry.registry',
                {'request_processors': [ctx_a, ctx_event]},
                clear=False,
            ),
        ):
            runner.run(data={}, commit=False)

        self.assertEqual(entered, ['proc_a'])
