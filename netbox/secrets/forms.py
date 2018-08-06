from __future__ import unicode_literals

from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
from django import forms
from django.db.models import Count
from taggit.forms import TagField

from dcim.models import Device
from extras.forms import AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldFilterForm, CustomFieldForm
from utilities.forms import BootstrapMixin, FilterChoiceField, FlexibleModelChoiceField, SlugField
from .models import Secret, SecretRole, UserKey


def validate_rsa_key(key, is_secret=True):
    """
    Validate the format and type of an RSA key.
    """
    try:
        key = RSA.importKey(key)
    except ValueError:
        raise forms.ValidationError("Invalid RSA key. Please ensure that your key is in PEM (base64) format.")
    except Exception as e:
        raise forms.ValidationError("Invalid key detected: {}".format(e))
    if is_secret and not key.has_private():
        raise forms.ValidationError("This looks like a public key. Please provide your private RSA key.")
    elif not is_secret and key.has_private():
        raise forms.ValidationError("This looks like a private key. Please provide your public RSA key.")
    try:
        PKCS1_OAEP.new(key)
    except Exception:
        raise forms.ValidationError("Error validating RSA key. Please ensure that your key supports PKCS#1 OAEP.")


#
# Secret roles
#

class SecretRoleForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = SecretRole
        fields = ['name', 'slug', 'users', 'groups']


class SecretRoleCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = SecretRole
        fields = SecretRole.csv_headers
        help_texts = {
            'name': 'Name of secret role',
        }


#
# Secrets
#

class SecretForm(BootstrapMixin, CustomFieldForm):
    plaintext = forms.CharField(
        max_length=65535,
        required=False,
        label='Plaintext',
        widget=forms.PasswordInput(attrs={'class': 'requires-session-key'})
    )
    plaintext2 = forms.CharField(
        max_length=65535,
        required=False,
        label='Plaintext (verify)',
        widget=forms.PasswordInput()
    )
    tags = TagField(required=False)

    class Meta:
        model = Secret
        fields = ['role', 'name', 'plaintext', 'plaintext2', 'tags']

    def __init__(self, *args, **kwargs):

        super(SecretForm, self).__init__(*args, **kwargs)

        # A plaintext value is required when creating a new Secret
        if not self.instance.pk:
            self.fields['plaintext'].required = True

    def clean(self):

        # Verify that the provided plaintext values match
        if self.cleaned_data['plaintext'] != self.cleaned_data['plaintext2']:
            raise forms.ValidationError({
                'plaintext2': "The two given plaintext values do not match. Please check your input."
            })


class SecretCSVForm(forms.ModelForm):
    device = FlexibleModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        help_text='Device name or ID',
        error_messages={
            'invalid_choice': 'Device not found.',
        }
    )
    role = forms.ModelChoiceField(
        queryset=SecretRole.objects.all(),
        to_field_name='name',
        help_text='Name of assigned role',
        error_messages={
            'invalid_choice': 'Invalid secret role.',
        }
    )
    plaintext = forms.CharField(
        help_text='Plaintext secret data'
    )

    class Meta:
        model = Secret
        fields = Secret.csv_headers
        help_texts = {
            'name': 'Name or username',
        }

    def save(self, *args, **kwargs):
        s = super(SecretCSVForm, self).save(*args, **kwargs)
        s.plaintext = str(self.cleaned_data['plaintext'])
        return s


class SecretBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Secret.objects.all(), widget=forms.MultipleHiddenInput)
    role = forms.ModelChoiceField(queryset=SecretRole.objects.all(), required=False)
    name = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['name']


class SecretFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Secret
    q = forms.CharField(required=False, label='Search')
    role = FilterChoiceField(
        queryset=SecretRole.objects.annotate(filter_count=Count('secrets')),
        to_field_name='slug'
    )


#
# UserKeys
#

class UserKeyForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = UserKey
        fields = ['public_key']
        help_texts = {
            'public_key': "Enter your public RSA key. Keep the private one with you; you'll need it for decryption. "
                          "Please note that passphrase-protected keys are not supported.",
        }

    def clean_public_key(self):
        key = self.cleaned_data['public_key']

        # Validate the RSA key format.
        validate_rsa_key(key, is_secret=False)

        return key


class ActivateUserKeyForm(forms.Form):
    _selected_action = forms.ModelMultipleChoiceField(queryset=UserKey.objects.all(), label='User Keys')
    secret_key = forms.CharField(label='Your private key', widget=forms.Textarea(attrs={'class': 'vLargeTextField'}))
