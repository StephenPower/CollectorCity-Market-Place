# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'PayPalShopSettings'
        db.create_table('payments_paypalshopsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('payer_id', self.gf('django.db.models.fields.CharField')(max_length=92)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('first_name', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('last_name', self.gf('django.db.models.fields.EmailField')(max_length=75)),
            ('perms', self.gf('picklefield.fields.PickledObjectField')(default=[])),
        ))
        db.send_create_signal('payments', ['PayPalShopSettings'])

        # Adding model 'PayPalToken'
        db.create_table('payments_paypaltoken', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Cart'])),
            ('token', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('confirmed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('payments', ['PayPalToken'])

        # Adding model 'GoogleCheckoutShopSettings'
        db.create_table('payments_googlecheckoutshopsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('merchant_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('merchant_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('payments', ['GoogleCheckoutShopSettings'])

        # Adding model 'GoogleCheckoutOrder'
        db.create_table('payments_googlecheckoutorder', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Sell'])),
            ('order_number', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('buyer_id', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('financial_state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('fulfillment_state', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('ready_to_ship', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
        ))
        db.send_create_signal('payments', ['GoogleCheckoutOrder'])

        # Adding model 'ManualPaymentShopSettings'
        db.create_table('payments_manualpaymentshopsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(default='')),
            ('instructions', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('payments', ['ManualPaymentShopSettings'])

        # Adding model 'BraintreeShopSettings'
        db.create_table('payments_braintreeshopsettings', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('merchant_id', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('public_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
            ('private_key', self.gf('django.db.models.fields.CharField')(max_length=40)),
        ))
        db.send_create_signal('payments', ['BraintreeShopSettings'])


    def backwards(self, orm):
        
        # Deleting model 'PayPalShopSettings'
        db.delete_table('payments_paypalshopsettings')

        # Deleting model 'PayPalToken'
        db.delete_table('payments_paypaltoken')

        # Deleting model 'GoogleCheckoutShopSettings'
        db.delete_table('payments_googlecheckoutshopsettings')

        # Deleting model 'GoogleCheckoutOrder'
        db.delete_table('payments_googlecheckoutorder')

        # Deleting model 'ManualPaymentShopSettings'
        db.delete_table('payments_manualpaymentshopsettings')

        # Deleting model 'BraintreeShopSettings'
        db.delete_table('payments_braintreeshopsettings')


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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
        },
        'payments.braintreeshopsettings': {
            'Meta': {'object_name': 'BraintreeShopSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'private_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'public_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'payments.googlecheckoutorder': {
            'Meta': {'object_name': 'GoogleCheckoutOrder'},
            'buyer_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'financial_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'fulfillment_state': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order_number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'ready_to_ship': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'sell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Sell']"})
        },
        'payments.googlecheckoutshopsettings': {
            'Meta': {'object_name': 'GoogleCheckoutShopSettings'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'merchant_id': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'merchant_key': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'payments.manualpaymentshopsettings': {
            'Meta': {'object_name': 'ManualPaymentShopSettings'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'payments.paypalshopsettings': {
            'Meta': {'object_name': 'PayPalShopSettings'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'payer_id': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'perms': ('picklefield.fields.PickledObjectField', [], {'default': '[]'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'payments.paypaltoken': {
            'Meta': {'object_name': 'PayPalToken'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Cart']"}),
            'confirmed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'token': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'sell.cart': {
            'Meta': {'object_name': 'Cart'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shippingdata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.ShippingData']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'sell.sell': {
            'Meta': {'object_name': 'Sell'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "'Manual Payment'", 'max_length': '255'}),
            'shippingdata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.ShippingData']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']", 'null': 'True'})
        },
        'sell.shippingdata': {
            'Meta': {'object_name': 'ShippingData'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
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

    complete_apps = ['payments']
