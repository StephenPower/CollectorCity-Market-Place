import datetime
import logging
import random

from urlparse import urlparse

from django.db import transaction
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

import braintree

import subscriptions
from django.shortcuts import render_to_response

if getattr(settings, 'BRAINTREE_PRODUCTION', False):
    BRAINTREE_ENVIROMENT = braintree.Environment.Production
else:
    BRAINTREE_ENVIROMENT = braintree.Environment.Sandbox

class BraintreeGateway():
    
    def __init__(self, merchant_id, public_key, private_key):
        #TODO: Remove this!!
        #merchant_id = settings.MERCHANT_ID
        #public_key = settings.PUBLIC_KEY
        #private_key = settings.PRIVATE_KEY
        #up to here
        braintree.Configuration.configure(
            BRAINTREE_ENVIROMENT,
            merchant_id,
            public_key,
            private_key
        )
    
    def __unicode__(self):
        return "BrainTree"
    
    def sandbox_get_valid_cc(self, card="Visa"):
        cc_numbers = {
              "Visa" : ["4111111111111111", "4005519200000004", "4009348888881881", "4012000033330026", "4012000077777777", "4012888888881881", "4217651111111119", "4500600000000061" ],
              "MasterCard" : ["5555555555554444"],
              "American Express" : ["378282246310005", "371449635398431"],
              "Discover" : ["6011111111111117"]
              }
        
        card_aux = cc_numbers[card]
        idx = random.randint(0, len(card_aux)-1)
        return card_aux[idx]
    
    def sandbox_get_invalid_cc(self, card="Visa"):
        
        cc_numbers = {
                     "Visa" : "4222222222222",
                     "MasterCard" : "5105105105105100",
                     "American Express" : "378734493671000",
                     "Discover" : "6011000990139424",
                     }        
        return cc_numbers[card]
    
    def sandbox_get_amount(self, type="SUCCESS"):
        """
        You can pass specific amounts to simulate different responses from the gateway.

        * Amounts between $0.01 - $1999.99 will simulate a successful authorization
        * Amounts between $2000.00 - $2046.00 and $3000.00 will decline with the coordinating Processor Response
        * Amounts between $2047.00 - $2099.00 will simulate the generic decline message Processor Declined.
        """
        
        if type == "SUCCESS":
            return float(random.randrange(0, 1999))
        elif type == "DECLINE":
            return float(random.randrange(2000, 2046))
        elif type == "PROCESSO_DECLINE":
            return float(random.randrange(2047, 2099))
        else:
            return float(15)
    
    def update_customer_shopname(self, customer_id, shop_id=None, shop_name=None):
        data = {}
        if shop_id is not None: data["website"] = shop_name
        if shop_name is not None: data["custom_fields"] = {"shop_id" : str(shop_id)}
        result = braintree.Customer.update(customer_id, data)
        return result
    
    
    def create_credit_card(self, customer_id, cc_number, cc_security_number, cc_expiration_date, street, city, state, zip):
        country = "US"
        result = braintree.CreditCard.create({
                "customer_id": customer_id,
                "number": cc_number,
                "cvv": cc_security_number,
                "expiration_date": cc_expiration_date,
                "billing_address": {
                    "street_address": street,
                    "extended_address": "-",
                    "locality": city,
                    "region": state,
                    "postal_code": zip,
                    "country_code_alpha2": country,
                    "country_code_alpha2": "US"
                }
        })
        return result

    def new_customer_credit_card(self, customer_id, cardholder_name, cc_number, cc_expiration_date, cc_security_number):
        result = braintree.CreditCard.create({
            "customer_id": customer_id,
            "number": cc_number,
            "cvv": cc_security_number,
            "expiration_date": cc_expiration_date,
            "cardholder_name": cardholder_name,
            "options": {
              "make_default": True,
              "verify_card": True,
            }
        })
        return result
    
    def create_customer(self, first_name, last_name, email, cc_number, cc_expiration_date, cc_security_number, street, city, state, zip, shop_name, shop_id):
        country="US"
        extra="-"
        result = braintree.Customer.create({
            "first_name": first_name,
            "last_name": last_name,            
            "email": email,
            "website": shop_name,
            #"company": "--",
            #"phone": "--",
            #"fax": "--",
            "credit_card": {
                "number": cc_number,
                "cvv": cc_security_number,
                "expiration_date": cc_expiration_date,
                "billing_address": {
                    "street_address": street,
                    "extended_address": extra,
                    "locality": city,
                    "region": state,
                    "postal_code": zip,
                    "country_code_alpha2": country,
                },
                "options": {
                    "verify_card": True,
                }
            },
            "custom_fields": {
                "shop_id" : str(shop_id),
            }
        })
        return result
        
    
    def delete_customer(self, customer_id):
        """ Delete the customer with customer_id in braintree """
        result = braintree.Customer.delete(customer_id)
        return result.is_success

    def create_subscription(self, plan_id, token):
        """ 
        Create a new subscription with the token associated to an specific customer (previously registered) 
        error = ErrorResult()
        error.is_success == False
        error.message == "Gateway Rejected: duplicate"
        
        @return: braintree.error_result.ErrorResult object | braintree.error_result.SuccessResult object
        """
        result = braintree.Subscription.create({
            "payment_method_token": token,
            "plan_id": plan_id,
        })
        return result
        
    def cancel_subscription(self, subscription_id):
        result = braintree.Subscription.cancel(subscription_id)
        return result

    def change_subscription(self, subscription_id, new_plan_id ):
        """ Change the customer subscription plan """
        new_price = "145.00"
        result = braintree.Subscription.update(subscription_id, {"plan_id" : new_plan_id , "price": new_price })
        return result
   
    def log_response(self, result):
        """ Process an API response """
        if result.is_success:
            logging.info( "success! tx_id : %s" % result.transaction.id)
        elif result.transaction:
            logging.info( "Error processing transaction:")
            logging.info( "  code: " + result.transaction.processor_response_code)
            logging.info( "  text: " + result.transaction.processor_response_text)
        else:
            for error in result.errors.deep_errors:
                logging.info("attribute: " + error.attribute)
                logging.info("code: " + error.code)
                logging.info("message: " + error.message)
        
        
        
    def charge_purchase(self, token, amount):
        """ Full example
        result = braintree.Transaction.sale({
          "amount": "10.00", #REQUIRED
          "order_id": "order id",
          "merchant_account_id": "a_merchant_account_id",
          "credit_card": {
            "number": "5105105105105100", #REQUIRED
            "expiration_date": "05/2012", #REQUIRED
            "cardholder_name": "The Cardholder",
            "cvv": "cvv"
          },
          "customer": {
            "first_name": "Drew",
            "last_name": "Smith",
            "company": "Braintree",
            "phone": "312-555-1234",
            "fax": "312-555-1235",
            "website": "http://www.example.com",
            "email": "drew@example.com"
          },
          "billing": {
            "first_name": "Paul",
            "last_name": "Smith",
            "company": "Braintree",
            "street_address": "1 E Main St",
            "extended_address": "Suite 403",
            "locality": "Chicago",
            "region": "Illinois",
            "postal_code": "60622",
            "country_code_alpha2": "US"
          },
          "shipping": {
            "first_name": "Jen",
            "last_name": "Smith",
            "company": "Braintree",
            "street_address": "1 E 1st St",
            "extended_address": "Suite 403",
            "locality": "Bartlett",
            "region": "Illinois",
            "postal_code": "60103",
            "country_code_alpha2": "US"
          },
          "options": {
            "submit_for_settlement": True, #REQUIRED
          }
        })
        """
        result = braintree.Transaction.sale({
            "payment_method_token": token,
            "amount": amount,
            #"credit_card": {"cvv": "100"} optional
        })
        
        return result

    def get_customer_details(self, customer_id):
        """ Return a customer Object with ID equals to customer_id """
        customer = braintree.Customer.find(customer_id)
        return customer
    
    def get_all_customers(self):
        """ Return all registered customers """
        collection = braintree.Customer.all()
        customers = []
        for customer in collection.items:
            customers.append(customer)
        
        return customers

    def get_subscription_details(self, subscription_id):
        """ Get a Subscription Object """
        subscription = braintree.Subscription.find(subscription_id)
        return subscription
    
    def get_all_subscriptions(self):
        """ Get All Subscriptions """
        search_results = braintree.Subscription.search(
                                braintree.SubscriptionSearch.status.in_list(
                                                braintree.Subscription.Status.Active,
                                                braintree.Subscription.Status.Canceled,
                                                braintree.Subscription.Status.Expired,
                                                braintree.Subscription.Status.PastDue,
                                                braintree.Subscription.Status.Pending))
        subscriptions = []
        for subscription in search_results.items:
            subscriptions.append(subscription)
        return subscriptions
        
    def get_active_subscriptions(self):
        """ Get All ACTIVE Subscriptions """
        search_results = braintree.Subscription.search([
                                braintree.SubscriptionSearch.status == braintree.Subscription.Status.Active
                                ])
        subscriptions = []
        for subscription in search_results.items:
            subscriptions.append(subscription)
        return subscriptions
    
    def get_past_due_subscriptions(self, days=2):
        """ Get back all subscriptions that were in past due status 'situacion de mora' """
        if days is None:
            search_results = braintree.Subscription.search([
                                braintree.SubscriptionSearch.days_past_due == days
                                ])
        else:
            search_results = braintree.Subscription.search([
                                braintree.SubscriptionSearch.days_past_due == days
                                ])
        subscriptions = []
        for subscription in search_results.items:
            subscriptions.append(subscription)
        return subscriptions
    
    def get_transaction_details(self, tx_id):
        transaction = braintree.Transaction.find(tx_id)
        return transaction
    
    def is_submitted_for_settlement(self, tx_id):
        transaction = self.get_transaction_details(tx_id)
        return transaction.status == braintree.Transaction.Status.SubmittedForSettlement
    
    def is_settled(self, tx_id):
        transaction = self.get_transaction_details(tx_id)
        return transaction.status == braintree.Transaction.Status.Settled

    def is_authorized(self, tx_id):
        transaction = self.get_transaction_details(tx_id)
        return transaction.status == braintree.Transaction.Status.Authorized
    
    def get_daily_transactions(self, day):
        day_init = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
        search_results = braintree.Transaction.search([
                                    braintree.TransactionSearch.created_at.between(day_init, day_end)
        ])
        result = [transaction for transaction in search_results.items]
        return result
    
    def get_transactions(self, day):
        day_init = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
        day_end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
        
        #FOR DEV
        #day_init = datetime.datetime(2010, 4, 1 , 0, 0, 0)
        #day_end = datetime.datetime(2011, 5, 10, 23, 59, 59)
        
        result = {}
        #----------- Declined Transactions
        declined_results = braintree.Transaction.search([
                braintree.TransactionSearch.processor_declined_at.between(day_init, day_end),                
        ])
        result['declined'] = [transaction for transaction in declined_results.items]
        
        #----------- Failed Transactions
        failed_results = braintree.Transaction.search([
                braintree.TransactionSearch.failed_at.between(day_init, day_end),                
        ])
        result['failed'] = [transaction for transaction in failed_results.items]
        
        #----------- Rejected Transactions
        gateway_rejected_results = braintree.Transaction.search([
                braintree.TransactionSearch.gateway_rejected_at.between(day_init, day_end),                
        ])
        result['rejected'] = [transaction for transaction in gateway_rejected_results.items]
        
        #----------- Settled Transactions
        gateway_settled_results = braintree.Transaction.search([
                braintree.TransactionSearch.settled_at.between(day_init, day_end),                
        ])
        result['settled'] = [transaction for transaction in gateway_settled_results.items]
        
        return result
    
    def get_expired_credit_cards(self):
        collection = braintree.CreditCard.expired()
        return collection
            
    def refund_transaction(self, tx_id):
        transaction = self.get_transaction_details(tx_id)
        result = braintree.Transaction.refund(transaction.id)
        result.transaction.type
        # "credit"
        result.transaction.id
        # e.g. "mtpw3x"
        return result
        
        
    def render_button(self, cart):
        import decimal
        context = decimal.Context(prec=20, rounding=decimal.ROUND_HALF_DOWN)
        decimal.setcontext(context)
        
        url = braintree.TransparentRedirect.url()
        #TODO: Replace this in production
        entry_point = "http://%s:8080%s" % (cart.shop.default_dns, reverse("braintree_confirm"))
        amount = cart.total_with_taxes()
        logging.warn(amount)
        amount = amount.quantize(decimal.Decimal('.01'))
        tr_data = braintree.Transaction.tr_data_for_sale({
            "transaction": {
                "type": "sale",
                "amount": str(amount),
#                "options": {
#                        "submit_for_settlement": True
#                }
            }
            
        }, entry_point)
        
        html = """
        <form action="%s" method="POST">
            <input type="hidden" name="tr_data" value="%s" />
            <label>Credit Card Number</label><input type="text" name="transaction[credit_card][number]" /><br/>
            <label>Expiration Date</label><input type="text" name="transaction[credit_card][expiration_date]" /><br/>
            <button class="primaryAction small awesome" type="submit">Pay</button>
        </form>
        """ % (url, tr_data)
        logging.debug("---- BRAINTREE FORM ----- \n%s" % html)
        return html
    
    def confirm_purchase(self, query):
        return braintree.TransparentRedirect.confirm(query)

    def submit_for_settlement(self, txn_id):
        result = braintree.Transaction.submit_for_settlement(txn_id)
        return result


def confirm(request):
    """
    Braintree will resend our form, and we should confirm resending the query (removing the leading ?)
    http://example.com/path?http_status=200&id=vgqssrhqhxfhgrwz&hash=0c3c641f1de3ed1c732c54cab367355350603b28
    """
    from payments.models import BraintreeShopSettings, BrainTreeTransaction
    
    shop = request.shop
    cart = request.cart
        
    query_string =  "http_status=%s&id=%s&kind=%s&hash=%s" % (request.GET['http_status'], request.GET['id'], request.GET['kind'], request.GET['hash'])
    
    braintree_settings = BraintreeShopSettings.objects.filter(shop = shop).get()
    gw = BraintreeGateway(braintree_settings.merchant_id, 
                          braintree_settings.public_key,
                          braintree_settings.private_key)
    
    result = gw.confirm_purchase(query_string)
    #Check if txn is authorized!
    if result.is_success:
        #TODO: At this point the transaction is authorized but NOT submitted for settlement, 
        #if we want, here we could do that. If this action must be done by shop owner, 
        #the transaction id must be saved in a model
        settled_result = gw.submit_for_settlement(result.transaction.id)
        logging.critical(settled_result)
        if settled_result.is_success:
            # submitted successfully
            #Close and clean the cart
            sell = cart.close("BrainTree")
            bt_txn = BrainTreeTransaction(sell=sell, transaction_id=result.transaction.id)
            bt_txn.save()
            #Set the sell payments as paid
            #sell.payment.pay()
            request.flash['message'] = "Braintree will process your payment. Once we received the confirmation we will ship your package."
            request.flash['severity'] = "success"
            return HttpResponseRedirect(reverse('payments_success'))
        else:
            if settled_result.message: logging.critical(settled_result.message)
            request.flash['message'] = "Payment Failed! " + settled_result.errors.deep_errors
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('my_shopping'))
        
    else:
        message = ""
        if result.transaction:
            code = result.transaction.processor_response_code
            text = result.transaction.processor_response_text
            message = "Payment Failed! %s.\[%s] %s" % (result.message, code, text)
            
        else:
            for error in result.errors.deep_errors:
                txt = "attribute: %s, code: %s. %s" (error.attribute, error.code, error.message)    
                message += txt + "\n"
                
        request.flash['message'] = message
        request.flash['severity'] = "error" 
        return HttpResponseRedirect(reverse('my_shopping'))
