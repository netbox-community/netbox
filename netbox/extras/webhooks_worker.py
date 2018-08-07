import hashlib
import hmac
import requests
import json

from django_rq import job
from rest_framework.utils.encoders import JSONEncoder

from extras.constants import WEBHOOK_CT_JSON, WEBHOOK_CT_X_WWW_FORM_ENCODED, OBJECTCHANGE_ACTION_CHOICES


@job('default')
def process_webhook(webhook, data, model_class, event, timestamp):
    """
    Make a POST request to the defined Webhook
    """
    payload = {
        'event': dict(OBJECTCHANGE_ACTION_CHOICES)[event].lower(),
        'timestamp': timestamp,
        'model': model_class._meta.model_name,
        'data': data
    }
    headers = {
        'Content-Type': webhook.get_http_content_type_display(),
    }
    params = {
        'method': 'POST',
        'url': webhook.payload_url,
        'headers': headers
    }

    if webhook.http_content_type == WEBHOOK_CT_JSON:
        params.update({'data': json.dumps(payload, cls=JSONEncoder)})
    elif webhook.http_content_type == WEBHOOK_CT_X_WWW_FORM_ENCODED:
        params.update({'data': payload})

    prepared_request = requests.Request(**params).prepare()

    if webhook.secret != '':
        # Sign the request with a hash of the secret key and its content.
        hmac_prep = hmac.new(
            key=webhook.secret.encode('utf8'),
            msg=prepared_request.body.encode('utf8'),
            digestmod=hashlib.sha512
        )
        prepared_request.headers['X-Hook-Signature'] = hmac_prep.hexdigest()

    with requests.Session() as session:
        session.verify = webhook.ssl_verification
        response = session.send(prepared_request)

    if response.status_code >= 200 and response.status_code <= 299:
        return 'Status {} returned, webhook successfully processed.'.format(response.status_code)
    else:
        raise requests.exceptions.RequestException(
            "Status {} returned, webhook FAILED to process.".format(response.status_code)
        )
