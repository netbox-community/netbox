from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA

from django import forms
from django.db.models import Count

from dcim.models import Device
from utilities.forms import BootstrapMixin, BulkImportForm, CSVDataField, SlugField

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
    except:
        raise forms.ValidationError("Error validating RSA key. Please ensure that your key supports PKCS#1 OAEP.")


#
# Secret roles
#

class SecretRoleForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = SecretRole
        fields = ['name', 'slug']


#
# Secrets
#

class SecretForm(forms.ModelForm, BootstrapMixin):
    private_key = forms.CharField(widget=forms.HiddenInput())
    plaintext = forms.CharField(max_length=65535, required=False, label='Plaintext')
    plaintext2 = forms.CharField(max_length=65535, required=False, label='Plaintext (verify)')

    class Meta:
        model = Secret
        fields = ['role', 'name', 'plaintext', 'plaintext2']

    def clean(self):
        validate_rsa_key(self.cleaned_data['private_key'])

    def clean_plaintext2(self):
        plaintext = self.cleaned_data['plaintext']
        plaintext2 = self.cleaned_data['plaintext2']
        if plaintext != plaintext2:
            raise forms.ValidationError("The two given plaintext values do not match. Please check your input.")


class SecretFromCSVForm(forms.ModelForm):
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False, to_field_name='name',
                                    error_messages={'invalid_choice': 'Device not found.'})
    role = forms.ModelChoiceField(queryset=SecretRole.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid secret role.'})
    plaintext = forms.CharField()

    class Meta:
        model = Secret
        fields = ['device', 'role', 'name', 'plaintext']

    def save(self, *args, **kwargs):
        s = super(SecretFromCSVForm, self).save(*args, **kwargs)
        s.plaintext = str(self.cleaned_data['plaintext'])
        return s


class SecretImportForm(BulkImportForm, BootstrapMixin):
    private_key = forms.CharField(widget=forms.HiddenInput())
    csv = CSVDataField(csv_form=SecretFromCSVForm)


class SecretBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Secret.objects.all(), widget=forms.MultipleHiddenInput)
    role = forms.ModelChoiceField(queryset=SecretRole.objects.all())
    name = forms.CharField(max_length=100, required=False)


def secret_role_choices():
    role_choices = SecretRole.objects.annotate(secret_count=Count('secrets'))
    return [(r.slug, u'{} ({})'.format(r.name, r.secret_count)) for r in role_choices]


class SecretFilterForm(forms.Form, BootstrapMixin):
    role = forms.MultipleChoiceField(required=False, choices=secret_role_choices)


#
# UserKeys
#

class UserKeyForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = UserKey
        fields = ['public_key']
        help_texts = {
            'public_key': "Enter your public RSA key. Keep the private one with you; you'll need it for decryption.",
        }

    def clean_public_key(self):
        key = self.cleaned_data['public_key']

        # Validate the RSA key format.
        validate_rsa_key(key, is_secret=False)

        return key


class ActivateUserKeyForm(forms.Form):
    _selected_action = forms.ModelMultipleChoiceField(queryset=UserKey.objects.all(), label='User Keys')
    secret_key = forms.CharField(label='Your private key', widget=forms.Textarea(attrs={'class': 'vLargeTextField'}))
