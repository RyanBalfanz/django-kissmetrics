# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        pass # already the right underlying field, just switching to IntegerField instead of FK.
    def backwards(self, orm):
        pass

    models = {
        'django_kissmetrics.events': {
            'Meta': {'object_name': 'Events'},
            '_data': ('django.db.models.fields.TextField', [], {'db_column': "'data'", 'blank': 'True'}),
            'action': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'}),
            'create_ts': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '64', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'user_id': ('django.db.models.fields.IntegerField', [], {'null': 'True'})
        }
    }

    complete_apps = ['django_kissmetrics']