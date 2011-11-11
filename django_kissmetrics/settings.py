from Crypto.Cipher import AES

from django.conf import settings

KISSMETRICS_API_KEY = getattr(settings, 'KISSMETRICS_API_KEY', '')

if not KISSMETRICS_API_KEY:
    raise Exception('You must define KISSMETRICS_API_KEY in your projects settings.py')

KISSMETRICS_IGNORE = getattr(settings, 'KISSMETRICS_IGNORE', False)