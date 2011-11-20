# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeaturesHelpText'
        db.create_table('support_featureshelptext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('auctions', self.gf('django.db.models.fields.TextField')()),
            ('wishlist', self.gf('django.db.models.fields.TextField')()),
            ('mailinglist', self.gf('django.db.models.fields.TextField')()),
            ('google_analytics', self.gf('django.db.models.fields.TextField')()),
            ('show_attendance', self.gf('django.db.models.fields.TextField')()),
            ('custom_dns', self.gf('django.db.models.fields.TextField')()),
            ('paypal', self.gf('django.db.models.fields.TextField')()),
            ('google_checkout', self.gf('django.db.models.fields.TextField')()),
            ('credit_card', self.gf('django.db.models.fields.TextField')()),
            ('manual_payment', self.gf('django.db.models.fields.TextField')()),
            ('theme_change', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('support', ['FeaturesHelpText'])


    def backwards(self, orm):
        
        # Deleting model 'FeaturesHelpText'
        db.delete_table('support_featureshelptext')


    models = {
        'support.featureshelptext': {
            'Meta': {'object_name': 'FeaturesHelpText'},
            'auctions': ('django.db.models.fields.TextField', [], {}),
            'credit_card': ('django.db.models.fields.TextField', [], {}),
            'custom_dns': ('django.db.models.fields.TextField', [], {}),
            'google_analytics': ('django.db.models.fields.TextField', [], {}),
            'google_checkout': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailinglist': ('django.db.models.fields.TextField', [], {}),
            'manual_payment': ('django.db.models.fields.TextField', [], {}),
            'paypal': ('django.db.models.fields.TextField', [], {}),
            'show_attendance': ('django.db.models.fields.TextField', [], {}),
            'theme_change': ('django.db.models.fields.TextField', [], {}),
            'wishlist': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['support']
