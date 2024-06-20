import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render, resolve_url
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import url_has_allowed_host_and_scheme, urlencode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View
from social_core.backends.utils import load_backends

from account.models import UserToken
from core.models import ObjectChange
from core.tables import ObjectChangeTable
from extras.models import Bookmark
from extras.tables import BookmarkTable
from netbox.authentication import get_auth_backend_display, get_saml_idps
from netbox.config import get_config
from netbox.views import generic
from users import forms, tables
from users.models import UserConfig
from utilities.views import register_model_view


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
        form = AuthenticationForm(request)

        if request.user.is_authenticated:
            logger = logging.getLogger('netbox.auth.login')
            return self.redirect_to_next(request, logger)

        return render(request, self.template_name, {
            'form': form,
            'auth_backends': self.get_auth_backends(request),
        })

    def post(self, request):
        logger = logging.getLogger('netbox.auth.login')
        form = AuthenticationForm(request, data=request.POST)

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
    template_name = 'account/profile.html'

    def get(self, request):

        # Compile changelog table
        changelog = ObjectChange.objects.valid_models().restrict(request.user, 'view').filter(
            user=request.user
        ).prefetch_related(
            'changed_object_type'
        )[:20]
        changelog_table = ObjectChangeTable(changelog)

        return render(request, self.template_name, {
            'changelog_table': changelog_table,
            'active_tab': 'profile',
        })


class UserConfigView(LoginRequiredMixin, View):
    template_name = 'account/preferences.html'

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

            messages.success(request, _("Your preferences have been updated."))
            response = redirect('account:preferences')

            # Set/clear language cookie
            if language := form.cleaned_data['locale.language']:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            else:
                response.delete_cookie(settings.LANGUAGE_COOKIE_NAME)

            return response

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'preferences',
        })


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'account/password.html'

    def get(self, request):
        # LDAP users cannot change their password here
        if getattr(request.user, 'ldap_username', None):
            messages.warning(request, "LDAP-authenticated user credentials cannot be changed within NetBox.")
            return redirect('account:profile')

        form = PasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'password',
        })

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('account:profile')

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'change_password',
        })


#
# Bookmarks
#

class BookmarkListView(LoginRequiredMixin, generic.ObjectListView):
    table = BookmarkTable
    template_name = 'account/bookmarks.html'

    def get_queryset(self, request):
        return Bookmark.objects.filter(user=request.user)

    def get_extra_context(self, request):
        return {
            'active_tab': 'bookmarks',
        }


#
# User views for token management
#

class UserTokenListView(LoginRequiredMixin, View):

    def get(self, request):
        tokens = UserToken.objects.filter(user=request.user)
        table = tables.UserTokenTable(tokens)
        table.configure(request)

        return render(request, 'account/token_list.html', {
            'tokens': tokens,
            'active_tab': 'api-tokens',
            'table': table,
        })


@register_model_view(UserToken)
class UserTokenView(LoginRequiredMixin, View):

    def get(self, request, pk):
        token = get_object_or_404(UserToken.objects.filter(user=request.user), pk=pk)
        key = token.key if settings.ALLOW_TOKEN_RETRIEVAL else None

        return render(request, 'account/token.html', {
            'object': token,
            'key': key,
        })


@register_model_view(UserToken, 'edit')
class UserTokenEditView(generic.ObjectEditView):
    queryset = UserToken.objects.all()
    form = forms.UserTokenForm
    default_return_url = 'account:usertoken_list'

    def alter_object(self, obj, request, url_args, url_kwargs):
        if not obj.pk:
            obj.user = request.user
        return obj


@register_model_view(UserToken, 'delete')
class UserTokenDeleteView(generic.ObjectDeleteView):
    queryset = UserToken.objects.all()
    default_return_url = 'account:usertoken_list'
