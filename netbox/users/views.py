import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View
from social_core.backends.utils import load_backends

from extras.models import ObjectChange
from extras.tables import ObjectChangeTable
from netbox.authentication import get_auth_backend_display, get_saml_idps
from netbox.config import get_config
from netbox.views import generic
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import NetBoxGroup, NetBoxUser, ObjectPermission, Token, UserConfig


#
# Login/logout
#

class LoginView(View):
    """
    Perform user authentication via the web UI.
    """
    template_name = 'login.html'

    @method_decorator(sensitive_post_parameters('password'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def gen_auth_data(self, name, url, params):
        display_name, icon_name = get_auth_backend_display(name)
        return {
            'display_name': display_name,
            'icon_name': icon_name,
            'url': f'{url}?{urlencode(params)}',
        }

    def get_auth_backends(self, request):
        auth_backends = []
        saml_idps = get_saml_idps()

        for name in load_backends(settings.AUTHENTICATION_BACKENDS).keys():
            url = reverse('social:begin', args=[name])
            params = {}
            if next := request.GET.get('next'):
                params['next'] = next
            if name.lower() == 'saml' and saml_idps:
                for idp in saml_idps:
                    params['idp'] = idp
                    data = self.gen_auth_data(name, url, params)
                    data['display_name'] = f'{data["display_name"]} ({idp})'
                    auth_backends.append(data)
            else:
                auth_backends.append(self.gen_auth_data(name, url, params))

        return auth_backends

    def get(self, request):
        form = forms.LoginForm(request)

        if request.user.is_authenticated:
            logger = logging.getLogger('netbox.auth.login')
            return self.redirect_to_next(request, logger)

        return render(request, self.template_name, {
            'form': form,
            'auth_backends': self.get_auth_backends(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.auth.login')
        form = forms.LoginForm(request, data=request.POST)

        if form.is_valid():
            logger.debug("Login form validation was successful")

            # If maintenance mode is enabled, assume the database is read-only, and disable updating the user's
            # last_login time upon authentication.
            if get_config().MAINTENANCE_MODE:
                logger.warning("Maintenance mode enabled: disabling update of most recent login time")
                user_logged_in.disconnect(update_last_login, dispatch_uid='update_last_login')

            # Authenticate user
            auth_login(request, form.get_user())
            logger.info(f"User {request.user} successfully authenticated")
            messages.success(request, f"Logged in as {request.user}.")

            # Ensure the user has a UserConfig defined. (This should normally be handled by
            # create_userconfig() on user creation.)
            if not hasattr(request.user, 'config'):
                config = get_config()
                UserConfig(user=request.user, data=config.DEFAULT_USER_PREFERENCES).save()

            return self.redirect_to_next(request, logger)

        else:
            logger.debug(f"Login form validation failed for username: {form['username'].value()}")

        return render(request, self.template_name, {
            'form': form,
            'auth_backends': self.get_auth_backends(request),
        })

    def redirect_to_next(self, request, logger):
        data = request.POST if request.method == "POST" else request.GET
        redirect_url = data.get('next', settings.LOGIN_REDIRECT_URL)

        if redirect_url and url_has_allowed_host_and_scheme(redirect_url, allowed_hosts=None):
            logger.debug(f"Redirecting user to {redirect_url}")
        else:
            if redirect_url:
                logger.warning(f"Ignoring unsafe 'next' URL passed to login form: {redirect_url}")
            redirect_url = reverse('home')

        return HttpResponseRedirect(redirect_url)


class LogoutView(View):
    """
    Deauthenticate a web user.
    """

    def get(self, request):
        logger = logging.getLogger('netbox.auth.logout')

        # Log out the user
        username = request.user
        auth_logout(request)
        logger.info(f"User {username} has logged out")
        messages.info(request, "You have logged out.")

        # Delete session key cookie (if set) upon logout
        response = HttpResponseRedirect(resolve_url(settings.LOGOUT_REDIRECT_URL))
        response.delete_cookie('session_key')

        return response


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
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    filterset_form = forms.UserFilterForm
    table = tables.UserTable


@register_model_view(NetBoxUser)
class UserView(generic.ObjectView):
    queryset = NetBoxUser.objects.all()
    template_name = 'users/user.html'

    def get_extra_context(self, request, instance):
        changelog = ObjectChange.objects.restrict(request.user, 'view').filter(user=request.user)[:20]
        changelog_table = ObjectChangeTable(changelog)

        return {
            'changelog_table': changelog_table,
        }


@register_model_view(NetBoxUser, 'edit')
class UserEditView(generic.ObjectEditView):
    queryset = NetBoxUser.objects.all()
    form = forms.UserForm


@register_model_view(NetBoxUser, 'delete')
class UserDeleteView(generic.ObjectDeleteView):
    queryset = NetBoxUser.objects.all()


class UserBulkEditView(generic.BulkEditView):
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable
    form = forms.UserBulkEditForm


class UserBulkImportView(generic.BulkImportView):
    queryset = NetBoxUser.objects.all()
    model_form = forms.UserImportForm


class UserBulkDeleteView(generic.BulkDeleteView):
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable


#
# Groups
#

class GroupListView(generic.ObjectListView):
    queryset = NetBoxGroup.objects.annotate(users_count=Count('user'))
    filterset = filtersets.GroupFilterSet
    filterset_form = forms.GroupFilterForm
    table = tables.GroupTable


@register_model_view(NetBoxGroup)
class GroupView(generic.ObjectView):
    queryset = NetBoxGroup.objects.all()
    template_name = 'users/group.html'


@register_model_view(NetBoxGroup, 'edit')
class GroupEditView(generic.ObjectEditView):
    queryset = NetBoxGroup.objects.all()
    form = forms.GroupForm


@register_model_view(NetBoxGroup, 'delete')
class GroupDeleteView(generic.ObjectDeleteView):
    queryset = NetBoxGroup.objects.all()


class GroupBulkImportView(generic.BulkImportView):
    queryset = NetBoxGroup.objects.all()
    model_form = forms.GroupImportForm


class GroupBulkDeleteView(generic.BulkDeleteView):
    queryset = NetBoxGroup.objects.annotate(users_count=Count('user'))
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
