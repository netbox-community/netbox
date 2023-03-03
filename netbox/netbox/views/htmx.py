from django.shortcuts import render
from django.views.generic import View

from dcim.forms import SiteFilterForm


class ObjectSelectorView(View):
    template_name = 'htmx/object_selector.html'

    def get(self, request):
        form_class = self._get_form_class()
        form = form_class(request.GET)

        return render(request, self.template_name, {
            'form': form,
        })

    def _get_form_class(self):
        # TODO: Determine form class from request parameters
        return SiteFilterForm
