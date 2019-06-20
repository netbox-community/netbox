from django.conf import settings
from django.contrib.auth.backends import ModelBackend


class ViewExemptModelBackend(ModelBackend):
    """
    Custom implementation of Django's stock ModelBackend which allows for the exemption of arbitrary models from view
    permission enforcement.
    """
    def has_perm(self, user_obj, perm, obj=None):

        # If this is a view permission, check whether the model has been exempted from enforcement
        try:
            app, codename = perm.split('.')
            action, model = codename.split('_')
            if action == 'view':
                if (
                    # All models are exempt from view permission enforcement
                    '*' in settings.EXEMPT_VIEW_PERMISSIONS
                ) or (
                    # This specific model is exempt from view permission enforcement
                    '{}.{}'.format(app, model) in settings.EXEMPT_VIEW_PERMISSIONS
                ):
                    return True
        except ValueError:
            pass

        return super().has_perm(user_obj, perm, obj)
