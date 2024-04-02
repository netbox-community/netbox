import logging

from django.contrib.auth.signals import user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver

from netbox.config import get_config
from users.models import User, UserConfig
from utilities.request import get_client_ip


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger = logging.getLogger('netbox.auth.login')
    username = credentials.get("username")
    if client_ip := get_client_ip(request):
        logger.info(f"Failed login attempt for username: {username} from {client_ip}")
    else:
        logger.warning(
            "Client IP address could not be determined for validation. Check that the HTTP server is properly "
            "configured to pass the required header(s)."
        )
        logger.info(f"Failed login attempt for username: {username}")


@receiver(post_save, sender=User)
def create_userconfig(instance, created, raw=False, **kwargs):
    """
    Automatically create a new UserConfig when a new User is created. Skip this if importing a user from a fixture.
    """
    if created and not raw:
        config = get_config()
        UserConfig(user=instance, data=config.DEFAULT_USER_PREFERENCES).save()
