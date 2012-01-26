from KISSmetrics import KM

from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.encoding import smart_str

from django_kissmetrics import models, log, settings

SESSION_KEY_KISSMETRICS = 'kissmetrics_tasks'

class KISSMetricTask(object):
    """
    Data class used to store server-side KISS events that need to be included on the next page load.
    """

    def __init__(self, action, name, data=None):
        self.action=action
        self.name=name
        self.data=data

    def toJS(self):
        """
        _kmq.push(['identify', 'bob@bob.com']);
        _kmq.push(['record', 'Viewed Homepage']);
        _kmq.push(['record', 'Signed Up', {'Plan':'Pro', 'Amount':99.95}]);
        _kmq.push(['set', {'gender':'male'}]);

        the following is not yet supported:
        _kmq.push(['alias', 'bob', 'bob@bob.com']);
        """
        str = "_kmq.push(['%s'" % self.action

        if self.name:
            str += ",'%s'" % self.name

        if self.data:
            arr = []

            for key,value in self.data.items():
                arr.append("'%s':'%s'" % (key, value,))
            str += ',{%s}' % ','.join(arr)

        str += ']);'
        return str

    def save(self, user_or_request):
        # try included here, so we can't crash the page
        try:
            # there are situations where we won't have a tracking number yet
            identity, user = get_identity_and_user(user_or_request) or 'unknown'

            models.Events.objects.create(
                action=self.name,
                data=self.data,
                identity=identity,
                type=self.action,
                user=user,
            )
        except:
            log.exception('Failed to record async event')

class KMWrapper(KM):
    """
    A wrapper for the KISS class, so that we can record events sent to KISS.
    """

    def record(self, action, props=None):
        if not props:
            props = {}
        log.info('Recording KM event `%s` with props=%s' % (action, props,))
        super(KMWrapper, self).record(action, props)

    def track_request(self, data, type):
        if settings.KISSMETRICS_TRACK_INTERNALLY:
            kissmetric = models.Events(
                data=data,
                identity=self._id,
                type=models.KISSMETRICS_TYPE_CHOICES.KISS_TYPE[type],
            )

            user = getattr(self, 'user')

            if user:
                kissmetric.user = user

            if 'e' == type:
                kissmetric.action=data['_n']

            kissmetric.save()

    def request(self, type, data, update=True):
        # we need to encode unicode data on its way out the door.
        type = smart_str(type)
        stringified = {}
        for k,v in data.items():
            stringified[smart_str(k)] = smart_str(v)
        self.track_request(data, type)
        super(KMWrapper, self).request(type, stringified, update)

class KMMock(KMWrapper):
    """
    A mock class used to prevent the recording of KISS events for some users.
    """

    def request(self, type, data, update=True):
        self.track_request(data, type)
        pass

def get_identity_from_cookie(request):
    """
    Attempts to find the KISS identity from the COOKIEs.
    """
    return request.COOKIES.get('km_ni', '') or request.COOKIES.get('km_ai', '')

def get_identity_and_user(user_or_request):
    """
    Fetches the identity and user from the user or request object.
    """
    user = None

    if isinstance(user_or_request, HttpRequest):
        if user_or_request.user.is_authenticated():
            user = user_or_request
            identity = user_or_request.id
        else:
            identity = get_identity_from_cookie(user_or_request)
    elif isinstance(user_or_request, User):
        user = user_or_request
        identity = user_or_request.id
    else:
        raise Exception('Invalid object passed into get_kiss_instance, should be request or user, but was %s' % type(user_or_request))

    if not identity:
        raise Exception('User is required for kissmetric tracking')
    return identity, user

def get_kissmetrics_instance(user_or_request):
    """
    Creates a kiss instance using a Django request or auth user object.
        If an auth user is provided that will be used as the identity
        If a request is provided and the user is authenticated, then it will use that as the identity
        Otherwise, it will attempt to find the kiss identity variables from the cookie
    """
    identity, user = get_identity_and_user(user_or_request)

    if (user and user.kissmetrics_ignore) or settings.KISSMETRICS_IGNORE:
        km = KMMock(settings.KISSMETRICS_API_KEY)
    else:
        km = KMWrapper(settings.KISSMETRICS_API_KEY)

    km.user = user
    km.identify(identity)
    return km

def queue_kissmetrics_task(request, task):
    """
    Queue a kissmetric task to show on next page load.
    """
    metrics = request.session.get(SESSION_KEY_KISSMETRICS, [])
    metrics.append(task)
    request.session[SESSION_KEY_KISSMETRICS] = metrics