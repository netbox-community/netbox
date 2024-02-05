import random
import string

from django.http import HttpResponse
from django.views.generic import View

from dcim.models import Site
from utilities.views import register_model_view
from .models import DummyModel
# Trigger registration of custom column
from .tables import mycol


class DummyModelsView(View):

    def get(self, request):
        instance_count = DummyModel.objects.count()
        return HttpResponse(f"Instances: {instance_count}")


class DummyModelAddView(View):

    def get(self, request):
        return HttpResponse(f"Create an instance")

    def post(self, request):
        instance = DummyModel(
            name=''.join(random.choices(string.ascii_lowercase, k=8)),
            number=random.randint(1, 100000)
        )
        instance.save()
        return HttpResponse(f"Instance created")


@register_model_view(Site, 'extra', path='other-stuff')
class ExtraCoreModelView(View):

    def get(self, request, pk):
        return HttpResponse("Success!")
