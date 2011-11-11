from django.contrib.auth.models import User
from django.test.client import Client
from django.utils.unittest.case import TestCase

from django_kissmetrics import KISSMetricTask, KMWrapper, KMMock, get_kissmetrics_instance, queue_kissmetrics_task

class MiscTestCase(TestCase):

    def setUp(self):
        first_name = 'delete'
        last_name = 'me'
        password = 'pass'
        username = '%s%s' % (first_name, last_name)
        self.user = User.objects.create(
            email='%s@votizen.com' % username,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

    def test_kissmetrics(self):
        self.assertFalse(self.user.kissmetrics_ignore)
        self.assertTrue(self.user.kissmetrics_ignore)

        client = Client()
        self.assertFalse(client.user.kissmetrics_ignore)

        o = KISSMetricTask('identify', 'bob@bob.com')
        self.assertEquals("_kmq.push(['identify','bob@bob.com']);", o.toJS())

        o = KISSMetricTask('record', 'Viewed Homepage')
        self.assertEquals("_kmq.push(['record','Viewed Homepage']);", o.toJS())

        o = KISSMetricTask('record', 'Signed Up', {'Plan':'Pro', 'Amount':99.95})
        self.assertEquals("_kmq.push(['record','Signed Up',{'Amount':'99.95','Plan':'Pro'}]);", o.toJS())

        o = KISSMetricTask('set', None, {'gender':'male'})
        self.assertEquals("_kmq.push(['set',{'gender':'male'}]);", o.toJS())

#        o = KISSMetricTask('alias', 'bob', 'bob@bob.com')
#        self.assertEquals("_kmq.push(['alias', 'bob', 'bob@bob.com']);", o.toJS())

    def test_get_kissmetrics_instance(self):
        self.client = Client()
        km_ai = '1234'
        km_ni = 'asdf'

        self.assertRaises(Exception, get_kissmetrics_instance, self.client)

        self.client.COOKIES['km_ai'] = km_ai
        self.client.COOKIES['km_ni'] = km_ni

        km = get_kissmetrics_instance(self.client)
        self.assertEquals(km_ni, km._id)

        self.client.login(username=self.user.username, password=password)
        km = get_kissmetrics_instance(self.client)
        self.assertEquals(self.user.id, km._id)