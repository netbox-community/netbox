from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from account.models import UserToken
from extras.models import Bookmark, ObjectChange
from extras.tables import BookmarkTable, ObjectChangeTable
from netbox.views import generic
from users import filtersets, forms, tables
from users.models import Token
from utilities.views import register_model_view


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

            messages.success(request, "Your preferences have been updated.")
            return redirect('account:preferences')

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
