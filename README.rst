This package handles configuring KISSmetrics in Django, as well server-side events. There is a simple
template, "django_kissmetrics/kissmetrics.html", that can be included in any HTML template where
you want to use client-side tracking. Queued tasks are used to store server-side events for client-side
recording; use this for tracking events before the kissmetrics JavaScript has been loaded.

Requires that you install kissmetrics first::

    https://github.com/kissmetrics/KISSmetrics


In your `settings.py` please include::

    KISSMETRICS_API_KEY = '{YOUR_KISSMETRICS_API_KEY}'


For server-side tracking::

    from django.contrib.auth.models import User
    from django_kissmetrics.base import get_kissmetrics_instance

    user = User.objects.get(id=1)

    # pass in a django user object
    km_inst = get_kissmetrics_instance(user)
    km_inst.record('{EVENT_NAME}', {OPTIONAL_EVENT_PROPERTIES})

    # pass in a django request object
    def my_view(request):
        km_inst = get_kissmetrics_instance(request)
        km_inst.record('{EVENT_NAME}', {OPTIONAL_EVENT_PROPERTIES})


For client-side tracking::

    {% include 'django_kissmetrics/kissmetrics.html' %}
    <script type="text/javascript">
    _kmq.push('record', '{EVENT_NAME}', {OPTIONAL_EVENT_PROPERTIES});
    </script>


For server-side to client-side tracking::

    from django_kissmetrics.base import KISSMetricTask, queue_kissmetrics_task

    def my_view(request):
        o = KISSMetricTask('record', '{EVENT_NAME}', {OPTIONAL_EVENT_PROPERTIES})
        queue_kissmetrics_task(request, o)


To track events you are sending KISS server-side in your own DB, add the following to your `settings.py`::

    KISSMETRICS_TRACK_INTERNALLY = True

    # also, run `python manage.py syncdb` before you start recording events


To globally turn off KISSmetrics, add the following in your `settings.py`::

    KISSMETRICS_IGNORE = True


Or you can turn off tracking for a single user by adding the following property before calling get_kissmetrics_instance::

    user = User.objects.get(id=1)
    user.kissmetrics_ignore = True
    get_kissmetrics_instance(user).record('this event will not record')

