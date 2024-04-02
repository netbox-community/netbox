from django.db.models import Count

from extras.models import ObjectChange
from extras.tables import ObjectChangeTable
from netbox.views import generic
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import Group, User, ObjectPermission, Token


#
# Tokens
#

class TokenListView(generic.ObjectListView):
    queryset = Token.objects.all()
    filterset = filtersets.TokenFilterSet
    filterset_form = forms.TokenFilterForm
    table = tables.TokenTable


@register_model_view(Token)
class TokenView(generic.ObjectView):
    queryset = Token.objects.all()


@register_model_view(Token, 'edit')
class TokenEditView(generic.ObjectEditView):
    queryset = Token.objects.all()
    form = forms.TokenForm


@register_model_view(Token, 'delete')
class TokenDeleteView(generic.ObjectDeleteView):
    queryset = Token.objects.all()


class TokenBulkImportView(generic.BulkImportView):
    queryset = Token.objects.all()
    model_form = forms.TokenImportForm


class TokenBulkEditView(generic.BulkEditView):
    queryset = Token.objects.all()
    table = tables.TokenTable
    form = forms.TokenBulkEditForm


class TokenBulkDeleteView(generic.BulkDeleteView):
    queryset = Token.objects.all()
    table = tables.TokenTable


#
# Users
#

class UserListView(generic.ObjectListView):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    filterset_form = forms.UserFilterForm
    table = tables.UserTable


@register_model_view(User)
class UserView(generic.ObjectView):
    queryset = User.objects.all()
    template_name = 'users/user.html'

    def get_extra_context(self, request, instance):
        changelog = ObjectChange.objects.restrict(request.user, 'view').filter(user=instance)[:20]
        changelog_table = ObjectChangeTable(changelog)

        return {
            'changelog_table': changelog_table,
        }


@register_model_view(User, 'edit')
class UserEditView(generic.ObjectEditView):
    queryset = User.objects.all()
    form = forms.UserForm


@register_model_view(User, 'delete')
class UserDeleteView(generic.ObjectDeleteView):
    queryset = User.objects.all()


class UserBulkEditView(generic.BulkEditView):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable
    form = forms.UserBulkEditForm


class UserBulkImportView(generic.BulkImportView):
    queryset = User.objects.all()
    model_form = forms.UserImportForm


class UserBulkDeleteView(generic.BulkDeleteView):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable


#
# Groups
#

class GroupListView(generic.ObjectListView):
    queryset = Group.objects.annotate(users_count=Count('user')).order_by('name')
    filterset = filtersets.GroupFilterSet
    filterset_form = forms.GroupFilterForm
    table = tables.GroupTable


@register_model_view(Group)
class GroupView(generic.ObjectView):
    queryset = Group.objects.all()
    template_name = 'users/group.html'


@register_model_view(Group, 'edit')
class GroupEditView(generic.ObjectEditView):
    queryset = Group.objects.all()
    form = forms.GroupForm


@register_model_view(Group, 'delete')
class GroupDeleteView(generic.ObjectDeleteView):
    queryset = Group.objects.all()


class GroupBulkImportView(generic.BulkImportView):
    queryset = Group.objects.all()
    model_form = forms.GroupImportForm


class GroupBulkEditView(generic.BulkEditView):
    queryset = Group.objects.all()
    filterset = filtersets.GroupFilterSet
    table = tables.GroupTable
    form = forms.GroupBulkEditForm


class GroupBulkDeleteView(generic.BulkDeleteView):
    queryset = Group.objects.annotate(users_count=Count('user')).order_by('name')
    filterset = filtersets.GroupFilterSet
    table = tables.GroupTable


#
# ObjectPermissions
#

class ObjectPermissionListView(generic.ObjectListView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    filterset_form = forms.ObjectPermissionFilterForm
    table = tables.ObjectPermissionTable


@register_model_view(ObjectPermission)
class ObjectPermissionView(generic.ObjectView):
    queryset = ObjectPermission.objects.all()
    template_name = 'users/objectpermission.html'


@register_model_view(ObjectPermission, 'edit')
class ObjectPermissionEditView(generic.ObjectEditView):
    queryset = ObjectPermission.objects.all()
    form = forms.ObjectPermissionForm


@register_model_view(ObjectPermission, 'delete')
class ObjectPermissionDeleteView(generic.ObjectDeleteView):
    queryset = ObjectPermission.objects.all()


class ObjectPermissionBulkEditView(generic.BulkEditView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
    form = forms.ObjectPermissionBulkEditForm


class ObjectPermissionBulkDeleteView(generic.BulkDeleteView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
