# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'FeaturesHelpText.add_new_pages'
        db.add_column('support_featureshelptext', 'add_new_pages', self.gf('django.db.models.fields.TextField')(default='Help text description here!'), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'FeaturesHelpText.add_new_pages'
        db.delete_column('support_featureshelptext', 'add_new_pages')


    models = {
        'support.featureshelptext': {
            'Meta': {'object_name': 'FeaturesHelpText'},
            'add_new_pages': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'auctions': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'credit_card': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'custom_dns': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'google_analytics': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'google_checkout': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailinglist': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'manual_payment': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'paypal': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'show_attendance': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'theme_change': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"}),
            'wishlist': ('django.db.models.fields.TextField', [], {'default': "'Help text description here!'"})
        }
    }

    complete_apps = ['support']
