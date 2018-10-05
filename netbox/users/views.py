from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.http import is_safe_url
from django.views.generic import View

from secrets.forms import UserKeyForm
from secrets.models import SessionKey, UserKey
from utilities.forms import ConfirmationForm
from .forms import LoginForm, PasswordChangeForm, TokenForm
from .models import Token


#
# Login/logout
#

class LoginView(View):
    template_name = 'login.html'

    def get(self, request):
        form = LoginForm(request)

        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():

            # Determine where to direct user after successful login
            redirect_to = request.POST.get('next', '')
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = reverse('home')

            # Authenticate user
            auth_login(request, form.get_user())
            messages.info(request, "Logged in as {}.".format(request.user))

            return HttpResponseRedirect(redirect_to)

        return render(request, self.template_name, {
            'form': form,
        })


class LogoutView(View):

    def get(self, request):

        # Log out the user
        auth_logout(request)
        messages.info(request, "You have logged out.")

        # Delete session key cookie (if set) upon logout
        response = HttpResponseRedirect(reverse('home'))
        response.delete_cookie('session_key')

        return response


#
# User profiles
#

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'users/profile.html'

    def get(self, request):

        return render(request, self.template_name, {
            'active_tab': 'profile',
        })


@method_decorator(login_required, name='dispatch')
class ChangePasswordView(View):
    template_name = 'users/change_password.html'

    def get(self, request):
        form = PasswordChangeForm(user=request.user)

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'change_password',
        })

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect('user:profile')

        return render(request, self.template_name, {
            'form': form,
            'active_tab': 'change_password',
        })


@method_decorator(login_required, name='dispatch')
class UserKeyView(View):
    template_name = 'users/userkey.html'

    def get(self, request):
        try:
            userkey = UserKey.objects.get(user=request.user)
        except UserKey.DoesNotExist:
            userkey = None

        return render(request, self.template_name, {
            'userkey': userkey,
            'active_tab': 'userkey',
        })


class UserKeyEditView(View):
    template_name = 'users/userkey_edit.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        try:
            self.userkey = UserKey.objects.get(user=request.user)
        except UserKey.DoesNotExist:
            self.userkey = UserKey(user=request.user)

        return super(UserKeyEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UserKeyForm(instance=self.userkey)

        return render(request, self.template_name, {
            'userkey': self.userkey,
            'form': form,
            'active_tab': 'userkey',
        })

    def post(self, request):
        form = UserKeyForm(data=request.POST, instance=self.userkey)
        if form.is_valid():
            uk = form.save(commit=False)
            uk.user = request.user
            uk.save()
            messages.success(request, "Your user key has been saved.")
            return redirect('user:userkey')

        return render(request, self.template_name, {
            'userkey': self.userkey,
            'form': form,
            'active_tab': 'userkey',
        })


@method_decorator(login_required, name='dispatch')
class SessionKeyDeleteView(LoginRequiredMixin, View):

    def get(self, request):

        sessionkey = get_object_or_404(SessionKey, userkey__user=request.user)
        form = ConfirmationForm()

        return render(request, 'users/sessionkey_delete.html', {
            'obj_type': sessionkey._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:userkey'),
        })

    def post(self, request):

        sessionkey = get_object_or_404(SessionKey, userkey__user=request.user)
        form = ConfirmationForm(request.POST)
        if form.is_valid():

            # Delete session key
            sessionkey.delete()
            messages.success(request, "Session key deleted")

            # Delete cookie
            response = redirect('user:userkey')
            response.delete_cookie('session_key')

            return response

        return render(request, 'users/sessionkey_delete.html', {
            'obj_type': sessionkey._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:userkey'),
        })


@method_decorator(login_required, name='dispatch')
class RecentActivityView(View):
    template_name = 'users/recent_activity.html'

    def get(self, request):

        return render(request, self.template_name, {
            'recent_activity': request.user.actions.all()[:50],
            'active_tab': 'recent_activity',
        })


#
# API tokens
#

class TokenListView(LoginRequiredMixin, View):

    def get(self, request):

        tokens = Token.objects.filter(user=request.user)

        return render(request, 'users/api_tokens.html', {
            'tokens': tokens,
            'active_tab': 'api_tokens',
        })


class TokenEditView(LoginRequiredMixin, View):

    def get(self, request, pk=None):

        if pk is not None:
            if not request.user.has_perm('users.change_token'):
                return HttpResponseForbidden()
            token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        else:
            if not request.user.has_perm('users.add_token'):
                return HttpResponseForbidden()
            token = Token(user=request.user)

        form = TokenForm(instance=token)

        return render(request, 'utilities/obj_edit.html', {
            'obj': token,
            'obj_type': token._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:token_list'),
        })

    def post(self, request, pk=None):

        if pk is not None:
            token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
            form = TokenForm(request.POST, instance=token)
        else:
            token = Token()
            form = TokenForm(request.POST)

        if form.is_valid():
            token = form.save(commit=False)
            token.user = request.user
            token.save()

            msg = "Modified token {}".format(token) if pk else "Created token {}".format(token)
            messages.success(request, msg)

            if '_addanother' in request.POST:
                return redirect(request.path)
            else:
                return redirect('user:token_list')

        return render(request, 'utilities/obj_edit.html', {
            'obj': token,
            'obj_type': token._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:token_list'),
        })


class TokenDeleteView(PermissionRequiredMixin, View):
    permission_required = 'users.delete_token'

    def get(self, request, pk):

        token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        initial_data = {
            'return_url': reverse('user:token_list'),
        }
        form = ConfirmationForm(initial=initial_data)

        return render(request, 'utilities/obj_delete.html', {
            'obj': token,
            'obj_type': token._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:token_list'),
        })

    def post(self, request, pk):

        token = get_object_or_404(Token.objects.filter(user=request.user), pk=pk)
        form = ConfirmationForm(request.POST)
        if form.is_valid():
            token.delete()
            messages.success(request, "Token deleted")
            return redirect('user:token_list')

        return render(request, 'utilities/obj_delete.html', {
            'obj': token,
            'obj_type': token._meta.verbose_name,
            'form': form,
            'return_url': reverse('user:token_list'),
        })
