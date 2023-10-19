from django.http import HttpResponse
from django.views.generic import View

from dcim.models import Site
from utilities.views import register_model_view
from .models import DummyModel


class DummyModelsView(View):

    def get(self, request):
        instance_count = DummyModel.objects.count()
        return HttpResponse(f"Instances: {instance_count}")


@register_model_view(Site, 'extra', path='other-stuff')
class ExtraCoreModelView(View):

    def get(self, request, pk):
        return HttpResponse("Success!")
