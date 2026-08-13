import uuid
from unittest.mock import patch

from django.test import RequestFactory, SimpleTestCase

from netbox.context import current_request, events_queue, query_cache
from netbox.context_managers import event_tracking


def _build_request():
    request = RequestFactory().get('/')
    request.id = uuid.uuid4()
    request.user = None
    return request


class EventTrackingTestCase(SimpleTestCase):
    """
    Verify that event_tracking() populates and restores its context variables.
    """
    def assertContextVarsRestored(self):
        self.assertIsNone(current_request.get())
        self.assertEqual(events_queue.get(), {})
        self.assertIsNone(query_cache.get())

    def test_context_vars_set_within_block(self):
        request = _build_request()

        with event_tracking(request):
            self.assertIs(current_request.get(), request)
            self.assertEqual(events_queue.get(), {})
            self.assertIsNotNone(query_cache.get())

        self.assertContextVarsRestored()

    def test_context_vars_restored_after_exception(self):
        request = _build_request()

        with self.assertRaises(RuntimeError):
            with event_tracking(request):
                raise RuntimeError('simulated view/script failure')

        self.assertContextVarsRestored()

    def test_events_flushed_on_success(self):
        request = _build_request()

        with patch('netbox.context_managers.flush_events') as flush_events:
            with event_tracking(request):
                events_queue.get()['foo'] = 'bar'

        flush_events.assert_called_once_with(['bar'])

    def test_events_not_flushed_after_exception(self):
        request = _build_request()

        with patch('netbox.context_managers.flush_events') as flush_events:
            with self.assertRaises(RuntimeError):
                with event_tracking(request):
                    events_queue.get()['foo'] = 'bar'
                    raise RuntimeError('simulated view/script failure')

        flush_events.assert_not_called()

    def test_nested_context_restores_outer_values(self):
        outer_request = _build_request()
        inner_request = _build_request()

        with patch('netbox.context_managers.flush_events'):
            with event_tracking(outer_request):
                outer_cache = query_cache.get()
                outer_queue = events_queue.get()
                outer_queue['outer'] = 'event'

                with event_tracking(inner_request):
                    self.assertIs(current_request.get(), inner_request)
                    self.assertIsNot(events_queue.get(), outer_queue)
                    self.assertEqual(events_queue.get(), {})

                # The outer request's context must be restored intact, including any events it had
                # already queued
                self.assertIs(current_request.get(), outer_request)
                self.assertIs(query_cache.get(), outer_cache)
                self.assertIs(events_queue.get(), outer_queue)
                self.assertEqual(events_queue.get(), {'outer': 'event'})

        self.assertContextVarsRestored()
