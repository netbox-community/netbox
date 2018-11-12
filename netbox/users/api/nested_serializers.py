from django.contrib.auth.models import User

from utilities.api import WritableNestedSerializer

_all_ = [
    'NestedUserSerializer',
]


#
# Users
#

class NestedUserSerializer(WritableNestedSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']
