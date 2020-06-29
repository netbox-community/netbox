# Report logging levels
LOG_DEFAULT = 0
LOG_SUCCESS = 10
LOG_INFO = 20
LOG_WARNING = 30
LOG_FAILURE = 40
LOG_LEVEL_CODES = {
    LOG_DEFAULT: 'default',
    LOG_SUCCESS: 'success',
    LOG_INFO: 'info',
    LOG_WARNING: 'warning',
    LOG_FAILURE: 'failure',
}

# Webhook content types
HTTP_CONTENT_TYPE_JSON = 'application/json'

# Registerable extras features
EXTRAS_FEATURES = [
    'custom_fields',
    'custom_links',
    'export_templates',
    'graphs',
    'job_results',
    'webhooks'
]
