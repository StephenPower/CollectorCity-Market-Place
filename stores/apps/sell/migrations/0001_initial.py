# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'ShippingData'
        db.create_table('sell_shippingdata', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('street_address', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=80, null=True, blank=True)),
            ('zip', self.gf('django.db.models.fields.CharField')(max_length=30, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('sell', ['ShippingData'])

        # Adding model 'Cart'
        db.create_table('sell_cart', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('shippingdata', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sell.ShippingData'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('sell', ['Cart'])

        # Adding model 'CartItem'
        db.create_table('sell_cartitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('cart', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Cart'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=2)),
            ('qty', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('sell', ['CartItem'])

        # Adding model 'Sell'
        db.create_table('sell_sell', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('bidder', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'], null=True)),
            ('completed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('shippingdata', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sell.ShippingData'], unique=True, null=True, blank=True)),
        ))
        db.send_create_signal('sell', ['Sell'])

        # Adding model 'SellItem'
        db.create_table('sell_sellitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('sell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Sell'])),
            ('price', self.gf('django.db.models.fields.DecimalField')(max_digits=11, decimal_places=2)),
            ('qty', self.gf('django.db.models.fields.IntegerField')()),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('sell', ['SellItem'])

        # Adding model 'Payment'
        db.create_table('sell_payment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('sell', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sell.Sell'], unique=True)),
            ('total', self.gf('django.db.models.fields.DecimalField')(default='0.0', max_digits=11, decimal_places=2)),
            ('state_actual', self.gf('django.db.models.fields.related.OneToOneField')(related_name='payment_history', unique=True, null=True, to=orm['sell.PaymentHistory'])),
        ))
        db.send_create_signal('sell', ['Payment'])

        # Adding model 'PaymentHistory'
        db.create_table('sell_paymenthistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Payment'])),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('sell', ['PaymentHistory'])

        # Adding model 'Shipping'
        db.create_table('sell_shipping', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('sell', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['sell.Sell'], unique=True)),
            ('state_actual', self.gf('django.db.models.fields.related.OneToOneField')(related_name='shipping_history', unique=True, null=True, to=orm['sell.ShippingHistory'])),
        ))
        db.send_create_signal('sell', ['Shipping'])

        # Adding model 'ShippingHistory'
        db.create_table('sell_shippinghistory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shipping', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sell.Shipping'])),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=2)),
        ))
        db.send_create_signal('sell', ['ShippingHistory'])


    def backwards(self, orm):
        
        # Deleting model 'ShippingData'
        db.delete_table('sell_shippingdata')

        # Deleting model 'Cart'
        db.delete_table('sell_cart')

        # Deleting model 'CartItem'
        db.delete_table('sell_cartitem')

        # Deleting model 'Sell'
        db.delete_table('sell_sell')

        # Deleting model 'SellItem'
        db.delete_table('sell_sellitem')

        # Deleting model 'Payment'
        db.delete_table('sell_payment')

        # Deleting model 'PaymentHistory'
        db.delete_table('sell_paymenthistory')

        # Deleting model 'Shipping'
        db.delete_table('sell_shipping')

        # Deleting model 'ShippingHistory'
        db.delete_table('sell_shippinghistory')


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
        'sell.cart': {
            'Meta': {'object_name': 'Cart'},
            'bidder': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'completed': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shippingdata': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['sell.ShippingData']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']", 'null': 'True'})
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
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'state_actual': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'shipping_history'", 'unique': 'True', 'null': 'True', 'to': "orm['sell.ShippingHistory']"})
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
        'sell.shippinghistory': {
            'Meta': {'object_name': 'ShippingHistory'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shipping': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sell.Shipping']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'})
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

    complete_apps = ['sell']
