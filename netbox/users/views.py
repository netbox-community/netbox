import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group, User, update_last_login
from django.contrib.auth.signals import user_logged_in
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
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
from utilities.forms import ConfirmationForm
from utilities.permissions import get_permission_for_model
from utilities.querysets import RestrictedQuerySet
from utilities.views import register_model_view
from . import filtersets, forms, tables
from .models import Token, UserConfig, NetBoxGroup, NetBoxUser, ObjectPermission


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
# User profiles
#

class ProfileView(LoginRequiredMixin, View):
    template_name = 'users/profile.html'

    def get(self, request):

        # Compile changelog table
        changelog = ObjectChange.objects.restrict(request.user, 'view').filter(user=request.user).prefetch_related(
            'changed_object_type'
        )[:20]
        changelog_table = ObjectChangeTable(changelog)

        return render(request, self.template_name, {
            'changelog_table': changelog_table,
            'active_tab': 'profile',
        })


class UserConfigView(LoginRequiredMixin, View):
    template_name = 'users/preferences.html'

    def get(self, request):
        userconfig = request.user.config
        form = forms.UserConfigForm(instance=userconfig)

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'preferences',
        })

    def post(self, request):
        userconfig = request.user.config
        form = forms.UserConfigForm(request.POST, instance=userconfig)

        if form.is_valid():
            form.save()

            messages.success(request, "Your preferences have been updated.")
            return redirect('users:preferences')

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'preferences',
        })


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'users/password.html'

    def get(self, request):
        # LDAP users cannot change their password here
        if getattr(request.user, 'ldap_username', None):
            messages.warning(request, "LDAP-authenticated user credentials cannot be changed within NetBox.")
            return redirect('users:profile')

        form = forms.PasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'password',
        })

    def post(self, request):
        form = forms.PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('users:profile')

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'change_password',
        })


#
# API tokens
#

class TokenListView(LoginRequiredMixin, View):

    def get(self, request):

        tokens = Token.objects.filter(user=request.user)
        table = tables.TokenTable(tokens)
        table.configure(request)

        return render(request, 'users/api_tokens.html', {
            'tokens': tokens,
            'active_tab': 'api-tokens',
            'table': table,
        })


@register_model_view(Token, 'edit')
class TokenEditView(LoginRequiredMixin, View):

    def get(self, request, pk=None):

        if pk:
            token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        else:
            token = Token(user=request.user)

        form = forms.TokenForm(instance=token)

        return render(request, 'generic/object_edit.html', {
            'object': token,
            'form': form,
            'return_url': reverse('users:token_list'),
        })

    def post(self, request, pk=None):

        if pk:
            token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
            form = forms.TokenForm(request.POST, instance=token)
        else:
            token = Token(user=request.user)
            form = forms.TokenForm(request.POST)

        if form.is_valid():

            token = form.save(commit=False)
            token.user = request.user
            token.save()

            msg = f"Modified token {token}" if pk else f"Created token {token}"
            messages.success(request, msg)

            if not pk and not settings.ALLOW_TOKEN_RETRIEVAL:
                return render(request, 'users/api_token.html', {
                    'object': token,
                    'key': token.key,
                    'return_url': reverse('users:token_list'),
                })
            elif '_addanother' in request.POST:
                return redirect(request.path)
            else:
                return redirect('users:token_list')

        return render(request, 'generic/object_edit.html', {
            'object': token,
            'form': form,
            'return_url': reverse('users:token_list'),
            'disable_addanother': not settings.ALLOW_TOKEN_RETRIEVAL
        })


@register_model_view(Token, 'delete')
class TokenDeleteView(LoginRequiredMixin, View):

    def get(self, request, pk):

        token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        initial_data = {
            'return_url': reverse('users:token_list'),
        }
        form = ConfirmationForm(initial=initial_data)

        return render(request, 'generic/object_delete.html', {
            'object': token,
            'form': form,
            'return_url': reverse('users:token_list'),
        })

    def post(self, request, pk):

        token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            token.delete()
            messages.success(request, "Token deleted")
            return redirect('users:token_list')

        return render(request, 'generic/object_delete.html', {
            'object': token,
            'form': form,
            'return_url': reverse('users:token_list'),
        })

#
# Users
#


class NetBoxUserListView(generic.ObjectListView):
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    filterset_form = forms.UserFilterForm
    table = tables.UserTable

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@register_model_view(NetBoxUser)
class NetBoxUserView(generic.ObjectView):
    queryset = NetBoxUser.objects.all()
    template_name = 'users/user.html'

    def get_extra_context(self, request, instance):
        # Compile changelog table
        changelog = ObjectChange.objects.restrict(request.user, 'view').filter(user=request.user).prefetch_related(
            'changed_object_type'
        )[:20]
        changelog_table = ObjectChangeTable(changelog)

        return {
            'changelog_table': changelog_table,
            'active_tab': 'user',
        }

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


@register_model_view(NetBoxUser, 'edit')
class NetBoxUserEditView(generic.ObjectEditView):
    queryset = NetBoxUser.objects.all()
    form = forms.UserForm


@register_model_view(NetBoxUser, 'delete')
class NetBoxUserDeleteView(generic.ObjectDeleteView):
    queryset = NetBoxUser.objects.all()

    def get_required_permission(self):
        return get_permission_for_model(User, 'delete')


class NetBoxUserBulkImportView(generic.BulkImportView):
    queryset = NetBoxUser.objects.all()
    model_form = forms.UserImportForm

    def get_required_permission(self):
        return get_permission_for_model(User, 'add')


class NetBoxUserBulkEditView(generic.BulkEditView):
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable
    form = forms.UserBulkEditForm

    def dispatch(self, request, *args, **kwargs):
        # breakpoint()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        # breakpoint()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # breakpoint()
        return super().post(request, *args, **kwargs)


class NetBoxUserBulkDeleteView(generic.BulkDeleteView):
    queryset = NetBoxUser.objects.all()
    filterset = filtersets.UserFilterSet
    table = tables.UserTable

    def get_required_permission(self):
        return get_permission_for_model(User, 'delete')


#
# Groups
#


class NetBoxGroupListView(generic.ObjectListView):
    queryset = NetBoxGroup.objects.all().annotate(users_count=Count('user'))
    filterset = filtersets.GroupFilterSet
    filterset_form = forms.GroupFilterForm
    table = tables.GroupTable


@register_model_view(NetBoxGroup)
class NetBoxGroupView(generic.ObjectView):
    queryset = NetBoxGroup.objects.all()
    template_name = 'users/group.html'

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'group',
        }


@register_model_view(NetBoxGroup, 'edit')
class NetBoxGroupEditView(generic.ObjectEditView):
    queryset = NetBoxGroup.objects.all()
    form = forms.GroupForm


@register_model_view(NetBoxGroup, 'delete')
class NetBoxGroupDeleteView(generic.ObjectDeleteView):
    queryset = NetBoxGroup.objects.all()


class NetBoxGroupBulkImportView(generic.BulkImportView):
    queryset = NetBoxGroup.objects.all()
    model_form = forms.GroupImportForm


# class NetBoxGroupBulkEditView(generic.BulkEditView):
#     queryset = NetBoxGroup.objects.all()
#     filterset = filtersets.GroupFilterSet
#     table = tables.GroupTable
#     form = forms.GroupBulkEditForm


class NetBoxGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = NetBoxGroup.objects.all()
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

    def get_extra_context(self, request, instance):
        return {
            'active_tab': 'objectpermission',
        }


@register_model_view(ObjectPermission, 'edit')
class ObjectPermissionEditView(generic.ObjectEditView):
    queryset = ObjectPermission.objects.all()
    form = forms.ObjectPermissionForm


@register_model_view(ObjectPermission, 'delete')
class ObjectPermissionDeleteView(generic.ObjectDeleteView):
    queryset = ObjectPermission.objects.all()


class ObjectPermissionBulkImportView(generic.BulkImportView):
    queryset = ObjectPermission.objects.all()
    model_form = forms.ObjectPermissionImportForm


class ObjectPermissionBulkEditView(generic.BulkEditView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
    form = forms.ObjectPermissionBulkEditForm


class ObjectPermissionBulkDeleteView(generic.BulkDeleteView):
    queryset = ObjectPermission.objects.all()
    filterset = filtersets.ObjectPermissionFilterSet
    table = tables.ObjectPermissionTable
