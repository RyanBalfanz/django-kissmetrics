from django_kissmetrics import models, settings, SESSION_KEY_KISSMETRICS, get_identity_from_cookie

def kissmetrics(request):
    """Set some upvote template variables that are expected on all requests"""
    identify_kiss = False
    kissmetrics_tasks = None
    user = request.user

    # these values only need to be processed for GET requests, should reduce thrash slightly
    if 'GET' == request.method:
        meta = request.META or {}
        path = meta.get('PATH_INFO', '')
        is_path_media_url = settings.MEDIA_URL and settings.MEDIA_URL in path
        is_path_static_url = settings.STATIC_URL and settings.STATIC_URL in path
        ignored_path = not path or 'favicon' in path or is_path_media_url or is_path_static_url or '__debug__/' in path

        # don't attempt to record if not a real page or skip_kiss is set
        if not ignored_path and not  meta.get('skip_kiss'):
            kissmetrics_tasks = request.session.pop(SESSION_KEY_KISSMETRICS, None)

            # don't identify, if already identified
            is_authenticated = user and user.is_authenticated()
            if is_authenticated and not request.session.get('identify_kiss'):
                identify_kiss = True
                request.session['identify_kiss'] = True

                # associate the user with the KISS identity
                if settings.KISSMETRICS_TRACK_INTERNALLY:
                    identity = get_identity_from_cookie(request)
                    models.Events.objects.filter(identity=identity).update(user=user)

    return {
        'identify_kiss': identify_kiss,
        'kissmetrics_tasks': kissmetrics_tasks,
    }
