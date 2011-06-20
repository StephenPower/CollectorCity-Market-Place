# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'MarketPlace'
        db.create_table('market_marketplace', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=92)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=92, db_index=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=92)),
            ('base_domain', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128)),
            ('template_prefix', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=92, db_index=True)),
        ))
        db.send_create_signal('market', ['MarketPlace'])

        # Adding model 'MarketCategory'
        db.create_table('market_marketcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('marketplace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketPlace'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=60, db_index=True)),
        ))
        db.send_create_signal('market', ['MarketCategory'])

        # Adding model 'MarketSubCategory'
        db.create_table('market_marketsubcategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('marketplace', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketPlace'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=60, db_index=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='subcategories', null=True, to=orm['market.MarketCategory'])),
        ))
        db.send_create_signal('market', ['MarketSubCategory'])

        # Adding unique constraint on 'MarketSubCategory', fields ['parent', 'slug']
        db.create_unique('market_marketsubcategory', ['parent_id', 'slug'])


    def backwards(self, orm):
        
        # Deleting model 'MarketPlace'
        db.delete_table('market_marketplace')

        # Deleting model 'MarketCategory'
        db.delete_table('market_marketcategory')

        # Deleting model 'MarketSubCategory'
        db.delete_table('market_marketsubcategory')

        # Removing unique constraint on 'MarketSubCategory', fields ['parent', 'slug']
        db.delete_unique('market_marketsubcategory', ['parent_id', 'slug'])


    models = {
        'market.marketcategory': {
            'Meta': {'object_name': 'MarketCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '60', 'db_index': 'True'})
        },
        'market.marketplace': {
            'Meta': {'object_name': 'MarketPlace'},
            'base_domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
        },
        'market.marketsubcategory': {
            'Meta': {'unique_together': "(('parent', 'slug'),)", 'object_name': 'MarketSubCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subcategories'", 'null': 'True', 'to': "orm['market.MarketCategory']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60', 'db_index': 'True'})
        }
    }

    complete_apps = ['market']
