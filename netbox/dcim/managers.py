from django.contrib.contenttypes.models import ContentType
from django.db.models import Manager


class CablePathManager(Manager):

    def create_for_endpoint(self, endpoint):
        ct = ContentType.objects.get_for_model(endpoint)
