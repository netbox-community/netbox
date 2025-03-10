from django.test import tag, TestCase

from extras.dashboard.widgets import ObjectListWidget


class ObjectListWidgetTests(TestCase):
    def test_widget_config_form_validates_model(self):
        model_info = 'extras.notification'
        form = ObjectListWidget.ConfigForm({'model': model_info})
        self.assertFalse(form.is_valid())

    @tag('regression')
    def test_widget_fails_gracefully(self):
        """
        Example:
        '2829fd9b-5dee-4c9a-81f2-5bd84c350a27': {
            'class': 'extras.ObjectListWidget',
            'color': 'indigo',
            'title': 'Object List',
            'config': {
                'model': 'extras.notification',
                'page_size': None,
                'url_params': None
            }
        }
        """
        config = {
            # 'class': 'extras.ObjectListWidget',  # normally popped off, left for clarity
            'color': 'yellow',
            'title': 'this should fail',
            'config': {
                'model': 'extras.notification',
                'page_size': None,
                'url_params': None,
            },
        }

        class Request:
            class User:
                def has_perm(self, *args, **kwargs):
                    return True

            user = User()

        mock_request = Request()
        widget = ObjectListWidget(id='2829fd9b-5dee-4c9a-81f2-5bd84c350a27', **config)
        rendered = widget.render(mock_request)
        self.assertTrue('Unable to load content. Invalid view name:' in rendered)
