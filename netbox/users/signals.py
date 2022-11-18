import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_login_failed


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    logger = logging.getLogger('netbox.auth.login')
    username = credentials.get("username")
    logger.info(f"Failed login attempt for username: {username}")
