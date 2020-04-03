from django.http import HttpResponse
from django.views.generic import View

from .models import DummyModel


class DummyModelsView(View):

    def get(self, request):
        instance_count = DummyModel.objects.count()
        return HttpResponse(f"Instances: {instance_count}")
