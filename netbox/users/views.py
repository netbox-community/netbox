from django.db.models import Count

from core.models import ObjectChange
from core.tables import ObjectChangeTable
from netbox.views import generic
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import Group, User, ObjectPermission, Token


#
# Tokens
#

@register_model_view(Token, 'list', path='', detail=False)
class TokenListView(generic.ObjectListView):
    queryset = Token.objects.all()
    filterset = filtersets.TokenFilterSet
    filterset_form = forms.TokenFilterForm
    table = tables.TokenTable


@register_model_view(Token)
class TokenView(generic.ObjectView):
    queryset = Token.objects.all()


@register_model_view(Token, 'add', detail=False)
@register_model_view(Token, 'edit')
class TokenEditView(generic.ObjectEditView):
    queryset = Token.objects.all()
    form = forms.TokenForm
    template_name = 'users/token_edit.html'


@register_model_view(Token, 'delete')
class TokenDeleteView(generic.ObjectDeleteView):
    queryset = Token.objects.all()


@register_model_view(Token, 'bulk_import', detail=False)
class TokenBulkImportView(generic.BulkImportView):
    queryset = Token.objects.all()
    model_form = forms.TokenImportForm


@register_model_view(Token, 'bulk_edit', path='edit', detail=False)
class TokenBulkEditView(generic.BulkEditView):
    queryset = Token.objects.all()
    table = tables.TokenTable
    form = forms.TokenBulkEditForm


@register_model_view(Token, 'bulk_delete', path='delete', detail=False)
class TokenBulkDeleteView(generic.BulkDeleteView):
    queryset = Token.objects.all()
    table = tables.TokenTable


#
# Users
#

@register_model_view(User, 'list', path='', detail=False)
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


@register_model_view(User, 'add', detail=False)
@register_model_view(User, 'edit')
class UserEditView(generic.ObjectEditView):
    queryset = User.objects.all()
    form = forms.UserForm


@register_model_view(User, 'delete')
class UserDeleteView(generic.ObjectDeleteView):
    queryset = User.objects.all()


@register_model_view(User, 'bulk_import', detail=False)
class UserBulkImportView(generic.BulkImportView):
    queryset = User.objects.all()
    model_form = forms.UserImportForm


@register_model_view(User, 'bulk_edit', path='edit', detail=False)
class UserBulkEditView(generic.BulkEditView):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable
    form = forms.UserBulkEditForm


@register_model_view(User, 'bulk_delete', path='delete', detail=False)
class UserBulkDeleteView(generic.BulkDeleteView):
    queryset = User.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable


#
# Groups
#

@register_model_view(Group, 'list', path='', detail=False)
class GroupListView(generic.ObjectListView):
    queryset = Group.objects.annotate(users_count=Count('user')).order_by('name')
    filterset = filtersets.GroupFilterSet
    filterset_form = forms.GroupFilterForm
    table = tables.GroupTable


@register_model_view(Group)
class GroupView(generic.ObjectView):
    queryset = Group.objects.all()
    template_name = 'users/group.html'


@register_model_view(Group, 'add', detail=False)
@register_model_view(Group, 'edit')
class GroupEditView(generic.ObjectEditView):
    queryset = Group.objects.all()
    form = forms.GroupForm


@register_model_view(Group, 'delete')
class GroupDeleteView(generic.ObjectDeleteView):
    queryset = Group.objects.all()


@register_model_view(Group, 'bulk_import', detail=False)
class GroupBulkImportView(generic.BulkImportView):
    queryset = Group.objects.all()
    model_form = forms.GroupImportForm


@register_model_view(Group, 'bulk_edit', path='edit', detail=False)
class GroupBulkEditView(generic.BulkEditView):
    queryset = Group.objects.all()
    filterset = filtersets.GroupFilterSet
    table = tables.GroupTable
    form = forms.GroupBulkEditForm


@register_model_view(Group, 'bulk_delete', path='delete', detail=False)
class GroupBulkDeleteView(generic.BulkDeleteView):
    queryset = Group.objects.annotate(users_count=Count('user')).order_by('name')
    filterset = filtersets.GroupFilterSet
    table = tables.GroupTable


#
# ObjectPermissions
#

@register_model_view(ObjectPermission, 'list', path='', detail=False)
class ObjectPermissionListView(generic.ObjectListView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    filterset_form = forms.ObjectPermissionFilterForm
    table = tables.ObjectPermissionTable


@register_model_view(ObjectPermission)
class ObjectPermissionView(generic.ObjectView):
    queryset = ObjectPermission.objects.all()
    template_name = 'users/objectpermission.html'


@register_model_view(ObjectPermission, 'add', detail=False)
@register_model_view(ObjectPermission, 'edit')
class ObjectPermissionEditView(generic.ObjectEditView):
    queryset = ObjectPermission.objects.all()
    form = forms.ObjectPermissionForm


@register_model_view(ObjectPermission, 'delete')
class ObjectPermissionDeleteView(generic.ObjectDeleteView):
    queryset = ObjectPermission.objects.all()


@register_model_view(ObjectPermission, 'bulk_edit', path='edit', detail=False)
class ObjectPermissionBulkEditView(generic.BulkEditView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
    form = forms.ObjectPermissionBulkEditForm


@register_model_view(ObjectPermission, 'bulk_delete', path='delete', detail=False)
class ObjectPermissionBulkDeleteView(generic.BulkDeleteView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
