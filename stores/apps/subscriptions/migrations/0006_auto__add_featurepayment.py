# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'FeaturePayment'
        db.create_table('subscriptions_featurepayment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('shop', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shops.Shop'])),
            ('transaction_id', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('price', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=11, decimal_places=2)),
            ('feature', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('subscriptions', ['FeaturePayment'])


    def backwards(self, orm):
        
        # Deleting model 'FeaturePayment'
        db.delete_table('subscriptions_featurepayment')


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
            'charge_on_card_as': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'contact_email': ('django.db.models.fields.EmailField', [], {'default': "'contact@yourstore.com'", 'max_length': '75'}),
            'contact_phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '92'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'template_prefix': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '92', 'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '92'})
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
        },
        'subscriptions.feature': {
            'Meta': {'object_name': 'Feature'},
            'auctions': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'credit_card': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'custom_dns': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'google_analytics': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'google_checkout': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mailinglist': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'manual_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'paypal': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'show_attendance': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'wishlist': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'})
        },
        'subscriptions.featurepayment': {
            'Meta': {'object_name': 'FeaturePayment'},
            'feature': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'transaction_id': ('django.db.models.fields.CharField', [], {'max_length': '10'})
        },
        'subscriptions.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['users.Profile']"}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.SubscriptionPlan']"}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'A'", 'max_length': '1'}),
            'subscription_id': ('django.db.models.fields.CharField', [], {'max_length': '6'})
        },
        'subscriptions.subscriptioncancelation': {
            'Meta': {'object_name': 'SubscriptionCancelation'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shop': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['shops.Shop']"}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.Subscription']"})
        },
        'subscriptions.subscriptionpayment': {
            'Meta': {'object_name': 'SubscriptionPayment'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'datetime': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['subscriptions.Subscription']"})
        },
        'subscriptions.subscriptionplan': {
            'Meta': {'object_name': 'SubscriptionPlan'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'additional_payment_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'additional_shipping_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'admin_accounts': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'auto_tax_integration': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'billing_period': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1', 'blank': 'True'}),
            'collect_emails': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'community_support_in_forums': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'community_wish_list': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'concurrent_auction_items': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'concurrent_store_items': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'create_auctions': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'custom_domain_name_fee': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'custom_migration': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'customizable_shipping_rates': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'email_support_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'google_analytics_support': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'listings_per_month': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'marketplace': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['market.MarketPlace']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'online_help_center': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'payment_methods': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'pictures_per_item': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'pictures_per_lot': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '1'}),
            'plan_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'secret_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'shopping_cart': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'show_attendance': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'}),
            'total_data_transfer': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'total_mbs_storage': ('django.db.models.fields.IntegerField', [], {'default': '50'}),
            'total_store_revenue': ('django.db.models.fields.DecimalField', [], {'max_digits': '11', 'decimal_places': '2'}),
            'trial_period': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'voice_support_price': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '11', 'decimal_places': '2'})
        },
        'users.profile': {
            'Meta': {'object_name': 'Profile'},
            'birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'photo': ('core.thumbs.ImageWithThumbsField', [], {'max_length': '100'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'street_address': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['subscriptions']
