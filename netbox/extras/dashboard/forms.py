from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from extras.choices import DashboardWidgetColorChoices
from netbox.registry import registry
from utilities.forms import add_blank_choice

__all__ = (
    'DashboardWidgetAddForm',
    'DashboardWidgetForm',
)


def get_widget_choices():
    return registry['widgets'].items()


class DashboardWidgetForm(forms.Form):
    title = forms.CharField(
        required=False
    )
    color = forms.ChoiceField(
        choices=add_blank_choice(DashboardWidgetColorChoices),
        required=False,
    )


class DashboardWidgetAddForm(DashboardWidgetForm):
    widget_class = forms.ChoiceField(
        choices=get_widget_choices,
        widget=forms.Select(
            attrs={
                'hx-get': reverse_lazy('extras:dashboardwidget_add'),
                'hx-target': '#widget_add_form',
            }
        ),
        label=_('Widget type')
    )
    field_order = ('widget_class', 'title', 'color')
