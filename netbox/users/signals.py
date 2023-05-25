import logging
from django.dispatch import receiver
from django.contrib.auth.signals import user_login_failed
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
