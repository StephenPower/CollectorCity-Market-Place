# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Preference.store_password'
        db.delete_column('preferences_preference', 'store_password')

        # Deleting field 'Preference.password'
        db.delete_column('preferences_preference', 'password')


    def backwards(self, orm):
        
        # Adding field 'Preference.store_password'
        db.add_column('preferences_preference', 'store_password', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True), keep_default=False)

        # Adding field 'Preference.password'
        db.add_column('preferences_preference', 'password', self.gf('django.db.models.fields.CharField')(default='', max_length=60, blank=True), keep_default=False)


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
        'market.marketplace': {
            'Meta': {'object_name': 'MarketPlace'},
            'base_domain': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128'}),
            'charge_on_card_as': ('django.db.models.fields.CharField', [], {'default': "''", 'unique': 'True', 'max_length': '255'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'default': "'contact@yourstore.com'", 'max_length': '75'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'privacy_policy': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
        },
        'preferences.dnsshop': {
            'Meta': {'object_name': 'DnsShop'},
            'dns': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'preferences.emailnotification': {
            'Meta': {'object_name': 'EmailNotification'},
            'body': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'type_notification': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        'preferences.preference': {
            'Meta': {'object_name': 'Preference'},
            'allow_open_auctions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_sessions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'checkout_currency': ('django.db.models.fields.CharField', [], {'default': "'USD'", 'max_length': '60'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "'City'", 'max_length': '60'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "'USA'", 'max_length': '60'}),
            'default_days': ('django.db.models.fields.CharField', [], {'default': '5', 'max_length': '1'}),
            'email': ('django.db.models.fields.EmailField', [], {'default': "'Email address when signed up'", 'max_length': '75'}),
            'google_analytics_account_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name_store': ('django.db.models.fields.CharField', [], {'default': "'Name of Store'", 'max_length': '60'}),
            'open_auto_extend': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "'Phone'", 'max_length': '60'}),
            'session_auto_extend': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'state': ('django.db.models.fields.CharField', [], {'default': "'State'", 'max_length': '60'}),
            'street': ('django.db.models.fields.CharField', [], {'default': "'Street'", 'max_length': '60'}),
            'taxes_same_state_store': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'taxes_to_shipping_fees': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "'Zip'", 'max_length': '30'})
        },
        'preferences.shippingitem': {
            'Meta': {'object_name': 'ShippingItem'},
            'from_item': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'to_item': ('django.db.models.fields.IntegerField', [], {})
        },
        'preferences.shippingprice': {
            'Meta': {'object_name': 'ShippingPrice'},
            'from_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'to_price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'})
        },
        'preferences.shippingweight': {
            'Meta': {'object_name': 'ShippingWeight'},
            'from_weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'to_weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'})
        },
        'preferences.shoppolicies': {
            'Meta': {'object_name': 'ShopPolicies'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'privacy_policy': ('django.db.models.fields.TextField', [], {}),
            'refund_policy': ('django.db.models.fields.TextField', [], {}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'terms_of_service': ('django.db.models.fields.TextField', [], {})
        },
        'preferences.taxstate': {
            'Meta': {'object_name': 'TaxState'},
            'apply_tax_to_shipping': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'state': ('django.contrib.localflavor.us.models.USStateField', [], {'max_length': '2'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'})
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

    complete_apps = ['preferences']
