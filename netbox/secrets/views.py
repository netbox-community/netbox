from __future__ import unicode_literals

import base64

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import View

from dcim.models import Device
from utilities.views import (
    BulkDeleteView, BulkEditView, BulkImportView, ObjectDeleteView, ObjectEditView, ObjectListView,
)
from . import filters, forms, tables
from .decorators import userkey_required
from .models import SecretRole, Secret, SessionKey


def get_session_key(request):
    """
    Extract and decode the session key sent with a request. Returns None if no session key was provided.
    """
    session_key = request.COOKIES.get('session_key', None)
    if session_key is not None:
        return base64.b64decode(session_key)
    return session_key


#
# Secret roles
#

class SecretRoleListView(ObjectListView):
    queryset = SecretRole.objects.annotate(secret_count=Count('secrets'))
    table = tables.SecretRoleTable
    template_name = 'secrets/secretrole_list.html'


class SecretRoleCreateView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'secrets.add_secretrole'
    model = SecretRole
    model_form = forms.SecretRoleForm
    default_return_url = 'secrets:secretrole_list'


class SecretRoleEditView(SecretRoleCreateView):
    permission_required = 'secrets.change_secretrole'


class SecretRoleBulkImportView(PermissionRequiredMixin, BulkImportView):
    permission_required = 'secrets.add_secretrole'
    model_form = forms.SecretRoleCSVForm
    table = tables.SecretRoleTable
    default_return_url = 'secrets:secretrole_list'


class SecretRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'secrets.delete_secretrole'
    queryset = SecretRole.objects.annotate(secret_count=Count('secrets'))
    table = tables.SecretRoleTable
    default_return_url = 'secrets:secretrole_list'


#
# Secrets
#

@method_decorator(login_required, name='dispatch')
class SecretListView(ObjectListView):
    queryset = Secret.objects.select_related('role', 'device')
    filter = filters.SecretFilter
    filter_form = forms.SecretFilterForm
    table = tables.SecretTable
    template_name = 'secrets/secret_list.html'


@method_decorator(login_required, name='dispatch')
class SecretView(View):

    def get(self, request, pk):

        secret = get_object_or_404(Secret, pk=pk)

        return render(request, 'secrets/secret.html', {
            'secret': secret,
        })


@permission_required('secrets.add_secret')
@userkey_required()
def secret_add(request, pk):

    # Retrieve device
    device = get_object_or_404(Device, pk=pk)

    secret = Secret(device=device)
    session_key = get_session_key(request)

    if request.method == 'POST':
        form = forms.SecretForm(request.POST, instance=secret)
        if form.is_valid():

            # We need a valid session key in order to create a Secret
            if session_key is None:
                form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

            # Create and encrypt the new Secret
            else:
                master_key = None
                try:
                    sk = SessionKey.objects.get(userkey__user=request.user)
                    master_key = sk.get_master_key(session_key)
                except SessionKey.DoesNotExist:
                    form.add_error(None, "No session key found for this user.")

                if master_key is not None:
                    secret = form.save(commit=False)
                    secret.plaintext = str(form.cleaned_data['plaintext'])
                    secret.encrypt(master_key)
                    secret.save()
                    messages.success(request, "Added new secret: {}.".format(secret))
                    if '_addanother' in request.POST:
                        return redirect('dcim:device_addsecret', pk=device.pk)
                    else:
                        return redirect('secrets:secret', pk=secret.pk)

    else:
        form = forms.SecretForm(instance=secret)

    return render(request, 'secrets/secret_edit.html', {
        'secret': secret,
        'form': form,
        'return_url': device.get_absolute_url(),
    })


@permission_required('secrets.change_secret')
@userkey_required()
def secret_edit(request, pk):

    secret = get_object_or_404(Secret, pk=pk)
    session_key = get_session_key(request)

    if request.method == 'POST':
        form = forms.SecretForm(request.POST, instance=secret)
        if form.is_valid():

            # Re-encrypt the Secret if a plaintext and session key have been provided.
            if form.cleaned_data['plaintext'] and session_key is not None:

                # Retrieve the master key using the provided session key
                master_key = None
                try:
                    sk = SessionKey.objects.get(userkey__user=request.user)
                    master_key = sk.get_master_key(session_key)
                except SessionKey.DoesNotExist:
                    form.add_error(None, "No session key found for this user.")

                # Create and encrypt the new Secret
                if master_key is not None:
                    secret = form.save(commit=False)
                    secret.plaintext = form.cleaned_data['plaintext']
                    secret.encrypt(master_key)
                    secret.save()
                    messages.success(request, "Modified secret {}.".format(secret))
                    return redirect('secrets:secret', pk=secret.pk)
                else:
                    form.add_error(None, "Invalid session key. Unable to encrypt secret data.")

            # We can't save the plaintext without a session key.
            elif form.cleaned_data['plaintext']:
                form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

            # If no new plaintext was specified, a session key is not needed.
            else:
                secret = form.save()
                messages.success(request, "Modified secret {}.".format(secret))
                return redirect('secrets:secret', pk=secret.pk)

    else:
        form = forms.SecretForm(instance=secret)

    return render(request, 'secrets/secret_edit.html', {
        'secret': secret,
        'form': form,
        'return_url': reverse('secrets:secret', kwargs={'pk': secret.pk}),
    })


class SecretDeleteView(PermissionRequiredMixin, ObjectDeleteView):
    permission_required = 'secrets.delete_secret'
    model = Secret
    default_return_url = 'secrets:secret_list'


class SecretBulkImportView(BulkImportView):
    permission_required = 'ipam.add_vlan'
    model_form = forms.SecretCSVForm
    table = tables.SecretTable
    template_name = 'secrets/secret_import.html'
    default_return_url = 'secrets:secret_list'
    widget_attrs = {'class': 'requires-session-key'}

    master_key = None

    def _save_obj(self, obj_form):
        """
        Encrypt each object before saving it to the database.
        """
        obj = obj_form.save(commit=False)
        obj.encrypt(self.master_key)
        obj.save()
        return obj

    def post(self, request):

        # Grab the session key from cookies.
        session_key = request.COOKIES.get('session_key')
        if session_key:

            # Attempt to derive the master key using the provided session key.
            try:
                sk = SessionKey.objects.get(userkey__user=request.user)
                self.master_key = sk.get_master_key(base64.b64decode(session_key))
            except SessionKey.DoesNotExist:
                messages.error(request, "No session key found for this user.")

            if self.master_key is not None:
                return super(SecretBulkImportView, self).post(request)
            else:
                messages.error(request, "Invalid private key! Unable to encrypt secret data.")

        else:
            messages.error(request, "No session key was provided with the request. Unable to encrypt secret data.")

        return render(request, self.template_name, {
            'form': self._import_form(request.POST),
            'fields': self.model_form().fields,
            'obj_type': self.model_form._meta.model._meta.verbose_name,
            'return_url': self.get_return_url(request),
        })


class SecretBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'secrets.change_secret'
    queryset = Secret.objects.select_related('role', 'device')
    filter = filters.SecretFilter
    table = tables.SecretTable
    form = forms.SecretBulkEditForm
    default_return_url = 'secrets:secret_list'


class SecretBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'secrets.delete_secret'
    queryset = Secret.objects.select_related('role', 'device')
    filter = filters.SecretFilter
    table = tables.SecretTable
    default_return_url = 'secrets:secret_list'
