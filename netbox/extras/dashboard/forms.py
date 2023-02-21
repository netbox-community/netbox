from django import forms

from utilities.forms import BootstrapMixin

__all__ = (
    'DashboardWidgetForm',
)


class DashboardWidgetForm(BootstrapMixin, forms.Form):
    title = forms.CharField(
        required=False
    )
