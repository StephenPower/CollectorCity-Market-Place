# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ProductType'
        db.create_table('inventory_producttype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('inventory', ['ProductType'])

        # Adding model 'Product'
        db.create_table('inventory_product', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketCategory'])),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketSubCategory'])),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('weight', self.gf('django.db.models.fields.DecimalField')(default='0', max_digits=11, decimal_places=2)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inventory.ProductType'], null=True, blank=True)),
        ))
        db.send_create_signal('inventory', ['Product'])

        # Adding model 'Coin'
        db.create_table('inventory_coin', (
            ('producttype_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['inventory.ProductType'], unique=True, primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketCategory'], null=True, blank=True)),
            ('subcategory', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['market.MarketSubCategory'], null=True, blank=True)),
            ('country_code', self.gf('django.db.models.fields.CharField')(default='us', max_length=2)),
            ('pcgs_number', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank='')),
            ('year_issued', self.gf('django.db.models.fields.CharField')(default='', max_length=24, blank='')),
            ('actual_year', self.gf('django.db.models.fields.CharField')(default='', max_length=24, blank='')),
            ('denomination', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('major_variety', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('die_variety', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('prefix', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('suffix', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('sort_order', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('heading', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('holder_variety', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('holder_variety_2', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank='')),
            ('additional_data', self.gf('django.db.models.fields.TextField')(default='', blank='')),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('inventory', ['Coin'])


    def backwards(self, orm):
        
        # Deleting model 'ProductType'
        db.delete_table('inventory_producttype')

        # Deleting model 'Product'
        db.delete_table('inventory_product')

        # Deleting model 'Coin'
        db.delete_table('inventory_coin')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '32'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'inventory.coin': {
            'Meta': {'object_name': 'Coin', '_ormbases': ['inventory.ProductType']},
            'actual_year': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '24', 'blank': "''"}),
            'additional_data': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': "''"}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketCategory']", 'null': 'True', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'default': "'us'", 'max_length': '2'}),
            'denomination': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': "''"}),
            'die_variety': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'heading': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'holder_variety': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'holder_variety_2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'major_variety': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'pcgs_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'prefix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'producttype_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['inventory.ProductType']", 'unique': 'True', 'primary_key': 'True'}),
            'sort_order': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketSubCategory']", 'null': 'True', 'blank': 'True'}),
            'suffix': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '60', 'blank': "''"}),
            'year_issued': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '24', 'blank': "''"})
        },
        'inventory.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketCategory']"}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'subcategory': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketSubCategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['inventory.ProductType']", 'null': 'True', 'blank': 'True'}),
            'weight': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '11', 'decimal_places': '2'})
        },
        'inventory.producttype': {
            'Meta': {'object_name': 'ProductType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'market.marketcategory': {
            'Meta': {'object_name': 'MarketCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '255'}),
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
            'order': ('django.db.models.fields.IntegerField', [], {'default': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'subcategories'", 'null': 'True', 'to': "orm['market.MarketCategory']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '60', 'db_index': 'True'})
        },
        'shops.shop': {
            'Meta': {'object_name': 'Shop'},
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'bids': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'39.29038,-76.61219'", 'max_length': '255'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['inventory']
