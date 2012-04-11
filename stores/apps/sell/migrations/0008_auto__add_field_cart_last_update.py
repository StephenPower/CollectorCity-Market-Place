# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Cart.last_update'
        db.add_column('sell_cart', 'last_update', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, default=datetime.datetime(2012, 2, 16, 10, 56, 1, 834657), blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Cart.last_update'
        db.delete_column('sell_cart', 'last_update')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
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
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
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
            'charge_on_card_as': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'default': "'contact@yourstore.com'", 'max_length': '75'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
        },
        'sell.cart': {
            'Meta': {'object_name': 'Cart'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'shippingdata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.ShippingData']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"})
        },
        'sell.cartitem': {
            'Meta': {'object_name': 'CartItem'},
            'cart': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Cart']"}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'qty': ('django.db.models.fields.IntegerField', [], {})
        },
        'sell.payment': {
            'Meta': {'object_name': 'Payment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sell': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.Sell']", 'unique': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'state_actual': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'payment_history'", 'unique': 'True', 'null': 'True', 'to': "orm['sell.PaymentHistory']"}),
            'total': ('django.db.models.fields.DecimalField', [], {'default': "'0.0'", 'max_digits': '11', 'decimal_places': '2'})
        },
        'sell.paymenthistory': {
            'Meta': {'object_name': 'PaymentHistory'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Payment']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'sell.sell': {
            'Meta': {'object_name': 'Sell'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'cancel': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'default': "'Manual Payment'", 'max_length': '255'}),
            'shippingdata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.ShippingData']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']", 'null': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '11', 'decimal_places': '2'}),
            'total_shipping': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '11', 'decimal_places': '2'}),
            'total_taxes': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '11', 'decimal_places': '2'}),
            'total_without_taxes': ('django.db.models.fields.DecimalField', [], {'default': "'0'", 'max_digits': '11', 'decimal_places': '2'})
        },
        'sell.sellitem': {
            'Meta': {'object_name': 'SellItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'price': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'qty': ('django.db.models.fields.IntegerField', [], {}),
            'sell': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Sell']"})
        },
        'sell.shipping': {
            'Meta': {'object_name': 'Shipping'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sell': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.Sell']", 'unique': 'True'}),
            'shipping_service': ('django.db.models.fields.CharField', [], {'default': "'Other'", 'max_length': '255'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'state_actual': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'shipping_history'", 'unique': 'True', 'null': 'True', 'to': "orm['sell.ShippingHistory']"}),
            'tracking_number': ('django.db.models.fields.CharField', [], {'default': "'--'", 'max_length': '255'})
        },
        'sell.shippingdata': {
            'Meta': {'object_name': 'ShippingData'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'sell.shippinghistory': {
            'Meta': {'object_name': 'ShippingHistory'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipping': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Shipping']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'shops.shop': {
            'Meta': {'object_name': 'Shop'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'admin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'bids': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_date_to_change_layout': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_date_to_post': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'default': "'39.29038,-76.61219'", 'max_length': '255'}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'views': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['sell']
