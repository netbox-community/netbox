from django.contrib.auth.models import Group, User

from utilities.api import WritableNestedSerializer

_all_ = [
    'NestedUserSerializer',
]


#
# Groups and users
#

class NestedGroupSerializer(WritableNestedSerializer):

    class Meta:
        model = Group
        fields = ['id', 'name']


class NestedUserSerializer(WritableNestedSerializer):

    class Meta:
        model = User
        fields = ['id', 'username']
