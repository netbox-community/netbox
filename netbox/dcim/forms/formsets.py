from django import forms
from django.utils.translation import gettext_lazy as _

__all__ = (
    'BaseVCMemberFormSet',
)


class BaseVCMemberFormSet(forms.BaseModelFormSet):

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Show members the user cannot change as read-only; disabled fields ignore submitted data
        if user is not None:
            permitted_pks = set(self.get_queryset().restrict(user, 'change').values_list('pk', flat=True))
            for form in self.forms:
                if form.instance.pk not in permitted_pks:
                    form.fields['vc_position'].disabled = True
                    form.fields['vc_priority'].disabled = True

    def clean(self):
        super().clean()

        # Check for duplicate VC position values
        vc_position_list = []
        for form in self.forms:
            vc_position = form.cleaned_data.get('vc_position')
            if vc_position:
                if vc_position in vc_position_list:
                    error_msg = _("A virtual chassis member already exists in position {vc_position}.").format(
                        vc_position=vc_position
                    )
                    form.add_error('vc_position', error_msg)
                vc_position_list.append(vc_position)
