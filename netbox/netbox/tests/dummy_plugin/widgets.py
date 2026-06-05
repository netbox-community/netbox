from extras.dashboard.utils import register_widget
from extras.dashboard.widgets import DashboardWidget


@register_widget
class DummyDashboardWidget(DashboardWidget):
    default_title = 'Dummy Dashboard Widget'
    description = 'A dummy dashboard widget for testing plugin registration.'

    def render(self, request):
        return 'Dummy dashboard widget content'
