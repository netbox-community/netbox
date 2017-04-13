import base64

from django.contrib import messages
from django.contrib.auth.decorators import permission_required, login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator

from dcim.models import Device
from utilities.views import BulkDeleteView, BulkEditView, ObjectDeleteView, ObjectEditView, ObjectListView

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


class SecretRoleEditView(PermissionRequiredMixin, ObjectEditView):
    permission_required = 'secrets.change_secretrole'
    model = SecretRole
    form_class = forms.SecretRoleForm

    def get_return_url(self, request, obj):
        return reverse('secrets:secretrole_list')


class SecretRoleBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'secrets.delete_secretrole'
    cls = SecretRole
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


@login_required
def secret(request, pk):

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
                    messages.success(request, u"Added new secret: {}.".format(secret))
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
                    secret.plaintext = str(form.cleaned_data['plaintext'])
                    secret.encrypt(master_key)
                    secret.save()
                    messages.success(request, u"Modified secret {}.".format(secret))
                    return redirect('secrets:secret', pk=secret.pk)
                else:
                    form.add_error(None, "Invalid session key. Unable to encrypt secret data.")

            # We can't save the plaintext without a session key.
            elif form.cleaned_data['plaintext']:
                form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

            # If no new plaintext was specified, a session key is not needed.
            else:
                secret = form.save()
                messages.success(request, u"Modified secret {}.".format(secret))
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


@permission_required('secrets.add_secret')
@userkey_required()
def secret_import(request):

    session_key = request.COOKIES.get('session_key', None)

    if request.method == 'POST':
        form = forms.SecretImportForm(request.POST)

        if session_key is None:
            form.add_error(None, "No session key was provided with the request. Unable to encrypt secret data.")

        if form.is_valid():

            new_secrets = []

            session_key = base64.b64decode(session_key)
            master_key = None
            try:
                sk = SessionKey.objects.get(userkey__user=request.user)
                master_key = sk.get_master_key(session_key)
            except SessionKey.DoesNotExist:
                form.add_error(None, "No session key found for this user.")

            if master_key is None:
                form.add_error(None, "Invalid private key! Unable to encrypt secret data.")
            else:
                try:
                    with transaction.atomic():
                        for secret in form.cleaned_data['csv']:
                            secret.encrypt(master_key)
                            secret.save()
                            new_secrets.append(secret)

                    table = tables.SecretTable(new_secrets)
                    messages.success(request, u"Imported {} new secrets.".format(len(new_secrets)))

                    return render(request, 'import_success.html', {
                        'table': table,
                    })

                except IntegrityError as e:
                    form.add_error('csv', "Record {}: {}".format(len(new_secrets) + 1, e.__cause__))

    else:
        form = forms.SecretImportForm()

    return render(request, 'secrets/secret_import.html', {
        'form': form,
        'return_url': reverse('secrets:secret_list'),
    })


class SecretBulkEditView(PermissionRequiredMixin, BulkEditView):
    permission_required = 'secrets.change_secret'
    cls = Secret
    filter = filters.SecretFilter
    form = forms.SecretBulkEditForm
    template_name = 'secrets/secret_bulk_edit.html'
    default_return_url = 'secrets:secret_list'


class SecretBulkDeleteView(PermissionRequiredMixin, BulkDeleteView):
    permission_required = 'secrets.delete_secret'
    cls = Secret
    filter = filters.SecretFilter
    default_return_url = 'secrets:secret_list'
