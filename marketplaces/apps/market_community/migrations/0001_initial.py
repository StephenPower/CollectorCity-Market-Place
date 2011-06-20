# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MarketPlaceAnnouncement'
        db.create_table('market_community_marketplaceannouncement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('marketplace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketPlace'])),
            ('posted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('posted_by', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('announcement', self.gf('django.db.models.fields.TextField')()),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('market_community', ['MarketPlaceAnnouncement'])

        # Adding model 'FAQCategory'
        db.create_table('market_community_faqcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('marketplace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketPlace'])),
            ('posted_on', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
        ))
        db.send_create_signal('market_community', ['FAQCategory'])

        # Adding model 'FAQEntry'
        db.create_table('market_community_faqentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market_community.FAQCategory'])),
            ('question', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('answer', self.gf('django.db.models.fields.TextField')()),
            ('anchor', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('market_community', ['FAQEntry'])


    def backwards(self, orm):
        
        # Deleting model 'MarketPlaceAnnouncement'
        db.delete_table('market_community_marketplaceannouncement')

        # Deleting model 'FAQCategory'
        db.delete_table('market_community_faqcategory')

        # Deleting model 'FAQEntry'
        db.delete_table('market_community_faqentry')


    models = {
        'market.marketplace': {
            'Meta': {'object_name': 'MarketPlace'},
            'base_domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
        },
        'market_community.faqcategory': {
            'Meta': {'object_name': 'FAQCategory'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'posted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'market_community.faqentry': {
            'Meta': {'object_name': 'FAQEntry'},
            'anchor': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'answer': ('django.db.models.fields.TextField', [], {}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market_community.FAQCategory']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'question': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'market_community.marketplaceannouncement': {
            'Meta': {'object_name': 'MarketPlaceAnnouncement'},
            'announcement': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'posted_by': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'posted_on': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['market_community']
