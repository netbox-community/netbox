from django.shortcuts import render
from django.views.generic import View

from dcim.filtersets import SiteFilterSet
from dcim.forms import SiteFilterForm
from dcim.models import Site


class ObjectSelectorView(View):
    template_name = 'htmx/object_selector.html'

    def get(self, request):
        form_class = self._get_form_class()
        form = form_class(request.GET)

        if '_search' in request.GET:
            # Return only search results
            model = self._get_model()
            filterset = self._get_filterset_class()

            queryset = model.objects.restrict(request.user)
            if filterset:
                queryset = filterset(request.GET, queryset, request=request).qs

            return render(request, 'htmx/object_selector_results.html', {
                'results': queryset,
            })

        return render(request, self.template_name, {
            'form': form,
        })

    def _get_model(self):
        # TODO: Determine model from request parameters
        return Site

    def _get_form_class(self):
        # TODO: Determine form class from model
        return SiteFilterForm

    def _get_filterset_class(self):
        # TODO: Determine filterset class from model
        return SiteFilterSet
