import json
import os
import sys
import threading
from contextlib import contextmanager
from pathlib import Path

try:
    import fcntl
except ImportError:
    fcntl = None

from django.apps import apps as django_apps
from django.db import connection
from django.test.utils import CaptureQueriesContext

__all__ = (
    'assert_expected_query_count',
)

UPDATE_ENV_VAR = 'UPDATE_QUERY_COUNTS'
BASELINE_FILENAME = 'query_counts.json'

_loaded_baselines = {}
_lock = threading.Lock()


def _is_update_mode():
    return bool(os.environ.get(UPDATE_ENV_VAR))


def _is_parallel_test_run():
    # Heuristic: inspects sys.argv for Django's --parallel flag. This is
    # sufficient for the project's standard `manage.py test` invocations but
    # will not detect parallelism introduced by other test runners.
    for arg in sys.argv:
        if arg == '--parallel' or arg.startswith('--parallel='):
            return True
    return False


def _baseline_path(app_label):
    app_config = django_apps.get_app_config(app_label)
    return Path(app_config.path) / 'tests' / BASELINE_FILENAME


def _load_baseline(app_label):
    with _lock:
        if app_label in _loaded_baselines:
            return _loaded_baselines[app_label]
        path = _baseline_path(app_label)
        if path.exists():
            with path.open() as f:
                data = json.load(f)
        else:
            data = {}
        _loaded_baselines[app_label] = data
        return data


def _record_update(app_label, key, count):
    # Write the baseline file synchronously rather than buffering until process
    # exit, so updates are not lost if the runner terminates via os._exit() or
    # a signal. An OS-level exclusive lock (where available) protects against
    # concurrent processes — e.g. two simultaneous update-mode invocations —
    # clobbering one another's writes.
    with _lock:
        path = _baseline_path(app_label)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('a+') as f:
            if fcntl is not None:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            f.seek(0)
            content = f.read()
            existing = json.loads(content) if content else {}
            existing[key] = count
            f.seek(0)
            f.truncate()
            json.dump(existing, f, indent=2, sort_keys=True)
            f.write('\n')


@contextmanager
def assert_expected_query_count(test_case, name):
    """
    Assert that the wrapped block performs the number of SQL queries recorded
    in the per-app baseline file (`<app>/tests/query_counts.json`).

    The baseline key is `<model_label>:<name>`. By default `<model_label>` is
    derived from `test_case.model._meta.model_name`. Test cases that use
    runtime-generated models with unstable names (e.g. names derived from a
    database primary-key sequence) can declare a ``query_count_model_label``
    class attribute to provide a stable, human-assigned label instead:

        class MyViewTestCase(ViewTestCases.PrimaryObjectViewTestCase):
            query_count_model_label = 'my-stable-label'

    When the `UPDATE_QUERY_COUNTS` environment variable is set, the assertion
    is skipped and the observed count is written back to the baseline file
    immediately. Update mode requires serial test execution (no --parallel).
    """
    model = test_case.model
    app_label = model._meta.app_label
    label = getattr(test_case, 'query_count_model_label', None)
    model_name = label if label is not None else model._meta.model_name
    key = f'{model_name}:{name}'

    if _is_update_mode():
        if _is_parallel_test_run():
            raise RuntimeError(
                f"{UPDATE_ENV_VAR}=1 cannot be combined with --parallel; "
                f"re-run serially to regenerate query-count baselines."
            )
        ctx = CaptureQueriesContext(connection)
        with ctx:
            yield
        _record_update(app_label, key, len(ctx.captured_queries))
        return

    baseline = _load_baseline(app_label)
    if key not in baseline:
        test_case.fail(
            f"No query-count baseline recorded for {app_label}/{key}. "
            f"Re-run with {UPDATE_ENV_VAR}=1 (serially) to record it."
        )

    expected = baseline[key]
    ctx = CaptureQueriesContext(connection)
    with ctx:
        yield
    actual = len(ctx.captured_queries)
    if actual != expected:
        sample = '\n'.join(
            f"  {i + 1}. {q['sql'][:240]}"
            for i, q in enumerate(ctx.captured_queries)
        )
        test_case.fail(
            f"Query count for {app_label}/{key} changed: "
            f"expected {expected}, got {actual}. "
            f"If this change is intentional, re-run with {UPDATE_ENV_VAR}=1 "
            f"to update the baseline.\nObserved queries:\n{sample}"
        )
