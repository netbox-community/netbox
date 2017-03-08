from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.utils.http import is_safe_url
from django.views.generic import View

from secrets.forms import UserKeyForm
from secrets.models import UserKey
from .forms import LoginForm, PasswordChangeForm
from .models import Token


#
# Login/logout
#

def login(request):

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():

            # Determine where to direct user after successful login
            redirect_to = request.POST.get('next', '')
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = reverse('home')

            # Authenticate user
            auth_login(request, form.get_user())
            messages.info(request, u"Logged in as {}.".format(request.user))

            return HttpResponseRedirect(redirect_to)

    else:
        form = LoginForm()

    return render(request, 'login.html', {
        'form': form,
    })


def logout(request):

    auth_logout(request)
    messages.info(request, u"You have logged out.")
    return HttpResponseRedirect(reverse('home'))


#
# User profiles
#

@login_required()
def profile(request):

    return render(request, 'users/profile.html', {
        'active_tab': 'profile',
    })


@login_required()
def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, u"Your password has been changed successfully.")
            return redirect('users:profile')

    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/change_password.html', {
        'form': form,
        'active_tab': 'change_password',
    })


@login_required()
def userkey(request):

    try:
        userkey = UserKey.objects.get(user=request.user)
    except UserKey.DoesNotExist:
        userkey = None

    return render(request, 'users/userkey.html', {
        'userkey': userkey,
        'active_tab': 'userkey',
    })


@login_required()
def userkey_edit(request):

    try:
        userkey = UserKey.objects.get(user=request.user)
    except UserKey.DoesNotExist:
        userkey = UserKey(user=request.user)

    if request.method == 'POST':
        form = UserKeyForm(data=request.POST, instance=userkey)
        if form.is_valid():
            uk = form.save(commit=False)
            uk.user = request.user
            uk.save()
            messages.success(request, u"Your user key has been saved.")
            return redirect('users:userkey')

    else:
        form = UserKeyForm(instance=userkey)

    return render(request, 'users/userkey_edit.html', {
        'userkey': userkey,
        'form': form,
        'active_tab': 'userkey',
    })


@login_required()
def recent_activity(request):

    return render(request, 'users/recent_activity.html', {
        'recent_activity': request.user.actions.all()[:50],
        'active_tab': 'recent_activity',
    })


#
# API tokens
#

class TokenList(LoginRequiredMixin, View):

    def get(self, request):

        tokens = Token.objects.filter(user=request.user)

        return render(request, 'users/api_tokens.html', {
            'tokens': tokens,
            'active_tab': 'api_tokens',
        })
