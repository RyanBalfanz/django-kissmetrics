from django.conf import settings

KISSMETRICS_API_KEY = getattr(settings, 'KISSMETRICS_API_KEY', '')

if not KISSMETRICS_API_KEY:
    raise Exception('You must define KISSMETRICS_API_KEY in your projects settings.py')

MEDIA_URL = getattr(settings, 'MEDIA_URL', '')
STATIC_URL = getattr(settings, 'STATIC_URL', '')

KISSMETRICS_IGNORE = getattr(settings, 'KISSMETRICS_IGNORE', False)
KISSMETRICS_TRACK_INTERNALLY = getattr(settings, 'KISSMETRICS_TRACK_INTERNALLY', False) # only supports DB tracking right now