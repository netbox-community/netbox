from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, QueryDict
from django.shortcuts import render
from django.utils.module_loading import import_string
from django.views.generic import View

# Static query_params from the originating field are sent under this prefix so they can be told apart from filters
# the user chooses in the modal. Both templates that emit these parameters must use the same prefix.
STATIC_PARAM_PREFIX = '_static_'


class ObjectSelectorView(LoginRequiredMixin, View):
    template_name = 'htmx/object_selector.html'

    def get(self, request):
        model = self._get_model(request.GET.get('_model', ''))

        # Constraints from the field's query_params. These are applied separately from the user's own filters, so
        # choosing another value in the visible form can only narrow the results, never widen them.
        static_params = {
            key[len(STATIC_PARAM_PREFIX):]: request.GET.getlist(key)
            for key in request.GET
            if key.startswith(STATIC_PARAM_PREFIX)
        }

        form_class = self._get_form_class(model)
        form = form_class(request.GET)

        if '_search' in request.GET:
            # Return only search results
            filterset = self._get_filterset_class(model)

            queryset = model.objects.restrict(request.user)
            if filterset:
                static_data = QueryDict(mutable=True)
                for key, values in static_params.items():
                    static_data.setlist(key, values)
                queryset = filterset(static_data, queryset, request=request).qs
                queryset = filterset(request.GET, queryset, request=request).qs

            return render(request, 'htmx/object_selector_results.html', {
                'results': queryset[:100],
            })

        return render(request, self.template_name, {
            'form': form,
            'model': model,
            'target_id': request.GET.get('target'),
            'static_params': static_params,
        })

    def _get_model(self, label):
        try:
            app_label, model_name = label.split('.')
            content_type = ContentType.objects.get_by_natural_key(app_label, model_name)
        except (ValueError, ObjectDoesNotExist):
            raise Http404
        return content_type.model_class()

    def _get_form_class(self, model):
        if hasattr(self, 'form_class'):
            return self.form_class
        app_label = model._meta.app_label
        class_name = f'{model.__name__}FilterForm'
        return import_string(f'{app_label}.forms.{class_name}')

    def _get_filterset_class(self, model):
        if hasattr(self, 'filterset_class'):
            return self.filterset_class
        app_label = model._meta.app_label
        class_name = f'{model.__name__}FilterSet'
        return import_string(f'{app_label}.filtersets.{class_name}')
