import copy

from django.test import TestCase

from utilities.forms.widgets import APISelect


class APISelectDeepcopyTest(TestCase):

    def test_static_params_survive_deepcopy(self):
        widget = APISelect()
        widget.add_query_params({'site_id': 1})
        copied_widget = copy.deepcopy(widget)

        # __deepcopy__ resets static_params but leaves the serialized attribute in place
        self.assertEqual(copied_widget.static_params, {})
        self.assertIn('data-static-params', copied_widget.attrs)

        context = copied_widget.get_context('site_id', None, {})
        self.assertEqual(context['static_params'], {'site_id': [1]})

    def test_static_params_empty_when_none_set(self):
        widget = APISelect()
        context = widget.get_context('site_id', None, {})
        self.assertEqual(context['static_params'], {})


class APISelectSelectorButtonTest(TestCase):

    def make_widget(self, query_params=None):
        widget = APISelect()
        widget.attrs['selector'] = 'dcim.device'
        if query_params:
            widget.add_query_params(query_params)
        return widget

    def render(self, widget):
        return widget.render('select_vm', None, attrs={'id': 'id_select_vm'})

    def test_button_includes_static_params(self):
        html = self.render(self.make_widget({'site_id': 1}))
        self.assertIn('&site_id=1', html)

    def test_button_includes_static_params_after_deepcopy(self):
        widget = copy.deepcopy(self.make_widget({'site_id': 1}))
        self.assertIn('&site_id=1', self.render(widget))

    def test_button_includes_every_value_of_a_multi_value_param(self):
        html = self.render(self.make_widget({'site_id': [1, 5]}))
        self.assertIn('&site_id=1', html)
        self.assertIn('&site_id=5', html)

    def test_button_has_no_params_without_query_params(self):
        html = self.render(self.make_widget())
        self.assertNotIn('&site_id=', html)
