# How long (in seconds) to cache successful and failed NDX API responses
CACHE_TIMEOUT = 300
ERROR_CACHE_TIMEOUT = 30

# Timeout (in seconds) for requests to the NDX API
REQUEST_TIMEOUT = 30

# The maximum number of results the NDX API returns per page
CATALOG_MAX_PAGE_SIZE = 200

# The maximum size (in bytes) of an image downloaded from the NDX API
IMAGE_MAX_SIZE = 10 * 1024 * 1024

# Image content types accepted from the NDX API, mapped to file extensions
IMAGE_EXTENSIONS = {
    'image/bmp': '.bmp',
    'image/gif': '.gif',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/tiff': '.tiff',
    'image/webp': '.webp',
}

# The maximum number of entries imported within a REST API request (larger imports are run as background jobs)
IMPORT_BACKGROUND_THRESHOLD = 5

# Additional time (in seconds) allowed for each entry imported by a background job
IMPORT_JOB_TIMEOUT_PER_ENTRY = 120

# Where users of the free tier can upgrade to obtain enrichment data
UPGRADE_URL = 'https://netboxlabs.com/contact-us/'
