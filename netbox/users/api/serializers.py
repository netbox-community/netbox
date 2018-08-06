from __future__ import unicode_literals

from django.contrib.auth.models import User

from utilities.api import WritableNestedSerializer


class NestedUserSerializer(WritableNestedSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']
