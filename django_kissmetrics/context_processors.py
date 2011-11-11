from django.conf import settings

from django_kissmetrics import SESSION_KEY_KISSMETRICS

def kissmetrics(request):
    """Set some upvote template variables that are expected on all requests"""
    identify_kiss = False
    user = request.user

    is_authenticated = user and user.is_authenticated()

    # these values only need to be processed for GET requests, should reduce thrash slightly
    if 'GET' == request.method:
        meta = request.META or {}
        ignored_path = 'favicon' in meta.get('PATH_INFO', '')

        if is_authenticated and not ignored_path and not request.session.get('identify_kiss') and not meta.get('skip_kiss'):
            identify_kiss = True
            request.session['identify_kiss'] = True

    kissmetrics_tasks = request.session.pop(SESSION_KEY_KISSMETRICS, None)

    return {
        'identify_kiss': identify_kiss,
        'kissmetrics_tasks': kissmetrics_tasks,
    }
