from KISSmetrics import KM
from logging import getLogger

from django.contrib.auth.models import User
from django.http import HttpRequest

from django_kissmetrics import models, settings

SESSION_KEY_KISSMETRICS = 'kissmetrics_tasks'

log = getLogger('django_kissmetrics')

class KISSMetricTask(object):
    '''
    Data class used to store server-side KISS events that need to be included on the next page load.
    '''

    def __init__(self, action, name, data=None):
        self.action=action
        self.name=name
        self.data=data

    def toJS(self):
        '''
        _kmq.push(['identify', 'bob@bob.com']);
        _kmq.push(['record', 'Viewed Homepage']);
        _kmq.push(['record', 'Signed Up', {'Plan':'Pro', 'Amount':99.95}]);
        _kmq.push(['set', {'gender':'male'}]);

        the following is not yet supported:
        _kmq.push(['alias', 'bob', 'bob@bob.com']);
        '''
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

class KMWrapper(KM):
    '''
    A wrapper for the KISS class, so that we can record events sent to KISS.
    '''

    def record(self, action, props={}):
        log.info('Recording KM event `%s` with props=%s' % (action, props,))
        super(KMWrapper, self).record(action, props)

    def request(self, type, data, update=True):
        if settings.KISSMETRICS_TRACK_INTERNALLY:
            kissmetric = models.Events(
                data=data,
                identity=self._id,
                type=models.KISSMETRICS_TYPE_CHOICES.KISS_TYPE[type],
            )

            if 'e' == type:
                kissmetric.action=data['_n']

            kissmetric.save()
        super(KMWrapper, self).request(type, data, update)

class KMMock(KMWrapper):
    '''
    A mock class used to prevent the recording of KISS events for some users.
    '''

    def request(self, type, data, update=True):
        pass

def get_identity_from_cookie(request):
    '''
    Attempts to find the KISS identity from the COOKIEs.
    '''
    return request.COOKIES.get('km_ni', '') or request.COOKIES.get('km_ai', '')

def get_kissmetrics_instance(user_or_request):
    '''
    Creates a kiss instance using a Django request or auth user object.
        If an auth user is provided that will be used as the identity
        If a request is provided and the user is authenticated, then it will use that as the indentity
        Otherwise, it will attempt to find the kiss identity variables from the cookie
    '''
    user = None

    if isinstance(user_or_request, HttpRequest):
        if user_or_request.user.is_authenticated():
            user = user_or_request
            indentity = user_or_request.id
        else:
            indentity = get_identity_from_cookie(user_or_request)
    elif isinstance(user_or_request, User):
        user = user_or_request
        indentity = user_or_request.id
    else:
        raise Exception('Invalid object passed into get_kiss_instance, should be request or user, but was %s' % type(user_or_request))

    if not indentity:
        raise Exception('User is required for kissmetric tracking')

    #
    if (user and user.kissmetrics_ignore) or settings.KISSMETRICS_IGNORE:
        km = KMMock(settings.KISSMETRICS_API_KEY)
    else:
        km = KMWrapper(settings.KISSMETRICS_API_KEY)

    km.identify(indentity)
    return km

def queue_kissmetrics_task(request, task):
    '''
    Queue a kissmetric task to show on next page load.
    '''
    metrics = request.session.get(SESSION_KEY_KISSMETRICS, [])
    metrics.append(task)
    request.session[SESSION_KEY_KISSMETRICS] = metrics