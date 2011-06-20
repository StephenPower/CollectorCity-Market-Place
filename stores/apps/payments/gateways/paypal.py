# -*- coding: utf-8 -*-
import urllib, md5, datetime
import logging
import decimal

from cgi import parse_qs
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils.translation import ugettext as _

from core.decorators import shop_required
from shops.models import Shop
from django.shortcuts import render_to_response
from django.template import loader
from django.template.context import RequestContext

from bidding.views import my_render

   
# Exception messages

TOKEN_NOT_FOUND_ERROR = "PayPal error occured. There is no TOKEN info to finish performing PayPal payment process. We haven't charged your money yet."
NO_PAYERID_ERROR = "PayPal error occured. There is no PAYERID info to finish performing PayPal payment process. We haven't charged your money yet."
GENERIC_PAYPAL_ERROR = "There occured an error while performing PayPal checkout process. We apologize for the inconvenience. We haven't charged your money yet."
GENERIC_PAYMENT_ERROR = "Transaction failed. Check out your order details again."
GENERIC_REFUND_ERROR = "An error occured, we can not perform your refund request"

class PayPalGateway(object):
    """
    Pluggable Python PayPal Driver that implements NVP (Name Value Pair) API methods.
    There are simply 3 main methods to be executed in order to finish the PayPal payment process.
    You explicitly need to define PayPal username, password and signature in your project's settings file.
    
    Those are:
    1) SetExpressCheckout
    2) GetExpressCheckoutDetails (optional)
    3) DoExpressCheckoutPayment
    """
    name = "paypal"
    
    def __init__(self, username, password, sign, debug = True):
        
        self.username  = username
        self.password  = password
        self.sign      = sign

        self.credientials = {
            "USER" : self.username,
            "PWD" : self.password,
            "SIGNATURE" : self.sign,
            "VERSION" : "63.0",
        }
        # Second step is to set the API end point and redirect urls correctly.
        if debug or getattr(settings, "PAYPAL_DEBUG", False):
            self.NVP_API_ENDPOINT    = "https://api-3t.sandbox.paypal.com/nvp"
            self.PAYPAL_REDIRECT_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="
            self.PAYPAL_WEBSCR_URL = "https://www.sandbox.paypal.com/cgi-bin/webscr"
        else:
            self.NVP_API_ENDPOINT    = "https://api-3t.paypal.com/nvp"
            self.PAYPAL_REDIRECT_URL = "https://www.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token="
            self.PAYPAL_WEBSCR_URL = "https://www.paypal.com/cgi-bin/webscr"

        # initialization
        self.signature = urllib.urlencode(self.credientials) + '&'
        self.setexpresscheckouterror = None
        self.getexpresscheckoutdetailserror = None
        self.doexpresscheckoutpaymenterror = None
        self.refundtransactionerror = None
        self.setaccesspermissionsdetailserror = None
        self.apierror = None
        self.api_response = None
        self.token = None
        self.response = None
        self.refund_response = None

    def _get_value_from_qs(self, qs, value):
        """
        Gets a value from a querystring dict
        This is a private helper function, so DO NOT call this explicitly.
        """
        raw = qs.get(value)
        if type(raw) == list:
            try:
                return raw[0]
            except KeyError:
                return None
        else:
            return raw


    def paypal_url(self, token = None):
        """
        Returns a 'redirect url' for PayPal payments.
        If token was null, this function MUST NOT return any URL.
        """
        token = token if token is not None else self.token
        if not token:
            return None
        return self.PAYPAL_REDIRECT_URL + token
    
    def redirect_url(self, cmd, token = None):
        
        token = token or self.token
        if token is None:
            return None
        
        urlparams = urllib.urlencode({
            'token': token,
            'cmd': cmd
        })
        return self.PAYPAL_WEBSCR_URL + '?' + urlparams 

    def SetExpressCheckout(self, payment_requests, return_url, cancel_url, **kwargs):
        """
        To set up an Express Checkout transaction, you must invoke the SetExpressCheckout API
        to provide sufficient information to initiate the payment flow and redirect to PayPal if the
        operation was successful.

        @payment_requests: dictionary with the paymentrequest see https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_r_SetExpressCheckout
        @return_url : should be in the format scheme://hostname[:uri (optional)]
        @cancel_url : should be in the format scheme://hostname[:uri (optional)]

        @returns bool

        If you want to add extra parameters, you can define them in **kwargs dict. For instance:
         - SetExpressCheckout(10.00, US, http://www.test.com/cancel/, http://www.test.com/return/, **{'SHIPTOSTREET': 'T Street', 'SHIPTOSTATE': 'T State'})
        """
        parameters = {
            'METHOD' : 'SetExpressCheckout',
            'NOSHIPPING' : 1,
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url,
        }
        
        
        parameters.update(payment_requests)
        parameters.update(kwargs)
        
        import logging
        logging.info(parameters)
        
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        state = self._get_value_from_qs(response_dict, "ACK")
        if state in ["Success", "SuccessWithWarning"]:
            self.token = self._get_value_from_qs(response_dict, "TOKEN")
            return True
        
        logging.debug(response_dict)
        self.setexpresscheckouterror = GENERIC_PAYPAL_ERROR
        self.apierror = self._get_value_from_qs(response_dict, "L_LONGMESSAGE0")
        return False


    """
    If SetExpressCheckout is successfull use TOKEN to redirect to the browser to the address BELOW:
    
     - https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_express-checkout&token=TOKEN (for development only URL)

    """

    def GetExpressCheckoutDetails(self, return_url, cancel_url, token = None):
        """
        This method performs the NVP API method that is responsible from getting the payment details.
        This returns True if successfully fetch the checkout details, otherwise returns False.
        All of the parameters are REQUIRED.

        @returns bool
        """
        token = self.token if token is None else token
        if token is None:
            self.getexpresscheckoutdetails = TOKEN_NOT_FOUND_ERROR
            return False

        parameters = {
            'METHOD' : "GetExpressCheckoutDetails",
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url,
            'TOKEN' : token,
        }
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        state = self._get_value_from_qs(response_dict, "ACK")
        if not state in ["Success", "SuccessWithWarning"]:
            self.getexpresscheckoutdetailserror = self._get_value_from_qs(response_dict, "L_SHORTMESSAGE0")
            self.apierror = self.getexpresscheckoutdetailserror
            return False

        return True


    def DoExpressCheckoutPayment(self, payment_requests, token = None, payerid = None, ** kwargs):
        """
        This method performs the NVP API method that is responsible from doing the actual payment.
        All of the parameters are REQUIRED.
        @currency: Look at 'https://cms.paypal.com/us/cgi-bin/?cmd=_render-content&content_ID=developer/e_howto_api_nvp_currency_codes'
        @amount : should be string with the following format '10.00'
        @token : token that will come from the result of SetExpressCheckout process.
        @payerid : payerid that will come from the url when PayPal redirects you after SetExpressCheckout process.


        @returns bool
        """
        if token is None:
            self.doexpresscheckoutpaymenterror = TOKEN_NOT_FOUND_ERROR
            return False

        if payerid is None:
            self.doexpresscheckoutpaymenterror = NO_PAYERID_ERROR
            return False

        parameters = {
            'METHOD' : "DoExpressCheckoutPayment",
            'PAYMENTACTION' : 'Sale',
            'TOKEN': token,
            'PAYERID' : payerid,
        }
        parameters.update(payment_requests)
        parameters.update(kwargs)
        
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])
        
        state = self._get_value_from_qs(response_tokens, "ACK")
        self.response = response_tokens
        self.api_response = response_tokens
        if not state in ["Success", "SuccessWithWarning"]:
            self.doexpresscheckoutpaymenterror = GENERIC_PAYMENT_ERROR
            self.apierror = self._get_value_from_qs(response_tokens, "L_LONGMESSAGE0")
            import logging
            logging.error(response_tokens)
            return False
        return True


    def RefundTransaction(self, transid, refundtype, currency = None, amount = None, note = "Dummy note for refund"):
        """
        Performs PayPal API method for refund.
        
        @refundtype: 'Full' or 'Partial'

        Possible Responses:
         {'ACK': 'Failure', 'TIMESTAMP': '2009-12-13T09:51:19Z', 'L_SEVERITYCODE0': 'Error', 'L_SHORTMESSAGE0':
         'Permission denied', 'L_LONGMESSAGE0': 'You do not have permission to refund this transaction', 'VERSION': '53.0',
         'BUILD': '1077585', 'L_ERRORCODE0': '10007', 'CORRELATIONID': '3d8fa24c46c65'}

         or
    
         {'REFUNDTRANSACTIONID': '9E679139T5135712L', 'FEEREFUNDAMT': '0.70', 'ACK': 'Success', 'TIMESTAMP': '2009-12-13T09:53:06Z',
         'CURRENCYCODE': 'AUD', 'GROSSREFUNDAMT': '13.89', 'VERSION': '53.0', 'BUILD': '1077585', 'NETREFUNDAMT': '13.19',
         'CORRELATIONID': '6c95d7f979fc1'}
        """

        if not refundtype in ["Full", "Partial"]:
            self.refundtransactionerror = "Wrong parameters given, We can not perform your refund request"
            return False
        
        parameters = {
            'METHOD' : "RefundTransaction",
            'TRANSACTIONID' : transid,
            'REFUNDTYPE' : refundtype,
        }
        
        if refundtype == "Partial":
            extra_values = {
                'AMT' : amount,
                'CURRENCYCODE' : currency,
                'NOTE' : note
            }
            parameters.update(extra_values)

        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_tokens = {}
        for token in response.split('&'):
            response_tokens[token.split("=")[0]] = token.split("=")[1]
            
        for key in response_tokens.keys():
            response_tokens[key] = urllib.unquote(response_tokens[key])

        state = self._get_value_from_qs(response_tokens, "ACK")
        self.refund_response = response_tokens
        self.api_response = response_tokens
        if not state in ["Success", "SuccessWithWarning"]:
            self.refundtransactionerror = GENERIC_REFUND_ERROR
            return False
        return True


    def GetPaymentResponse(self):
        return self.response

    def GetRefundResponse(self):
        return self.refund_response
    
    def GetAccessPermissionDetails(self, token=None):
        """
            Retrieves status of the permissions being requested from a user

        @return: (success, response)
        @type: tuple
        """
        token = self.token if token is None else token
        if token is None:
            self.getexpresscheckoutdetails = TOKEN_NOT_FOUND_ERROR
            return (False, None)

        parameters = {
            'METHOD' : "GetAccessPermissionDetails",
            'TOKEN' : token,
        }
        query_string = self.signature + urllib.urlencode(parameters)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        state = self._get_value_from_qs(response_dict, "ACK")
        if not state in ["Success", "SuccessWithWarning"]:
            self.getexpresscheckoutdetailserror = self._get_value_from_qs(response_dict, "L_SHORTMESSAGE0")
            self.apierror = self.getexpresscheckoutdetailserror
            return (False, response_dict)

        return (True, response_dict)
        
    def SetAccessPermissions(self, return_url, cancel_url, logout_url, 
                             required_permissions=None, optional_permissions=None):
        """
            Sets up a request to authorize permissions
            
            @rtype: tuple
            @return: (success, response)
        """
        
        parameters = {
            'METHOD' : "SetAccessPermissions",
            'RETURNURL' : return_url,
            'CANCELURL' : cancel_url,
            'LOGOUTURL' : logout_url
        }
        
        for i, perm in enumerate(required_permissions or []):
            parameters["L_requiredaccesspermissions%d" % i] = perm
        
        for i, perm in enumerate(optional_permissions or []):
            parameters["L_optionalaccesspermissions%d" % i] = perm
        
        logging.info(parameters)
        
        query_string = self.signature + urllib.urlencode(parameters)
        logging.info(query_string)
        response = urllib.urlopen(self.NVP_API_ENDPOINT, query_string).read()
        response_dict = parse_qs(response)
        self.api_response = response_dict
        state = self._get_value_from_qs(response_dict, "ACK")
        if not state in ["Success", "SuccessWithWarning"]:
            logging.info(response_dict)
            self.setaccesspermissionsdetailserror = self._get_value_from_qs(response_dict, "L_SHORTMESSAGE0")
            self.apierror = self.getexpresscheckoutdetailserror
            return (False, self.api_response)
        
        self.token = self._get_value_from_qs(response_dict, "TOKEN")
        return (True, self.api_response)
    
    def UpdateAccessPermissions(self):
        """
            Removes permissions for a user
        """
        pass 

    
    def render_button(self):
        return """
        <h3>PayPal</h3>
        <a href="%s"><img src="%simg/paypal-button.gif"/></a>
        """ % (reverse('payments_paypal_paynow'), settings.MEDIA_URL)
        
@shop_required    
def cancel(request):
    return HttpResponseRedirect(reverse('payments_cancel'))

@shop_required    
def success(request):    
    from payments.gateways.paypal import PayPalGateway
    from payments.models import PayPalShopSettings, PayPalToken, PayPalTransaction
    from preferences.models import Preference
    from sell.templatetags.sell_tags import money_format

    
    if request.method == 'GET':
        payerid = request.GET.get('PayerID', None)
        token = request.GET.get('token', None)
    else:
        payerid = request.POST.get('PayerID', None)
        token = request.POST.get('token', None)
    
    if None in (token, payerid):
        request.flash['message'] = unicode(_("Payment failed, try other method."))
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('my_shopping'))
    
    shop = request.shop   
    paypal_settings = PayPalShopSettings.objects.filter(shop = shop).get()
    profile = request.user.get_profile()
    
    
    try:
        paypaltoken = PayPalToken.objects.filter(token=token).get()
    except PayPalToken.DoesNotExist:
        request.flash['message'] = unicode(_("Payment failed, try other method."))
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('my_shopping'))

    if paypaltoken.confirmed == True:
        request.flash['message'] = unicode(_("Payment is already confirmed!"))
        request.flash['severity'] = "notice"
        return HttpResponseRedirect(reverse('my_shopping'))

    cart = paypaltoken.cart
    #currency = Preference.get_preference(shop).checkout_currency
    total_amount = "%0.2f" % cart.total_with_taxes()
    
    
    if request.method != 'POST':
        
        t = loader.get_template('payments/payment_paypal_confirm.html')
        c = RequestContext(request, {
                                     'payerid': payerid,
                                     'token': token,
                                    })
        block = (t.render(c))
        
        param = {'total_amount': money_format(total_amount, shop),
                 'paypaltoken': paypaltoken,
                 'cart': cart,
                 'cancel_url': reverse('payments_cancel'),
                 'form_paypal_confirm': block,
                }
        
        return HttpResponse(my_render(request, param, 'payment_paypal_confirm'))        
    
    
    action = request.POST.get('action', 'cancel').lower()
    
    if action == 'confirm':
        
        paypal_gw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                                  password=settings.PAYPAL_PASSWORD,
                                  sign=settings.PAYPAL_SIGNATURE,
                                  debug=settings.PAYPAL_DEBUG)
       
        token_data = paypal_gw.GetExpressCheckoutDetails("http://www.google.com", "http://www.google.com", paypaltoken.token)
        ack = paypal_gw.api_response['ACK'][0]
        
        try:
            amount = decimal.Decimal(paypal_gw.api_response['AMT'][0])
        except KeyError:
            logging.critical("Fail when trying to read the payment amount. The API response don't have an AMT key. RESPONSE: %s" % paypal_gw.api_response)    
            request.flash['message'] = unicode(_("We have found an error when trying to validate your purchase!"))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('my_shopping'))
        
        if ack != "Success":
            request.flash['message'] = unicode(_("Fail when trying to validate your PayPal Token. Please contact admin to complete your purchase!"))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('my_shopping'))
        
        if amount != cart.total_with_taxes():
            request.flash['message'] = unicode(_("You have authorized us to charge you just $%s, but you want buy $%s! Please contact admin if you think this is a mistake!" % (amount, cart.total_with_taxes())))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('my_shopping'))
    
        payment_request = {
            'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
            'PAYMENTREQUEST_0_AMT': "%0.2f" % cart.total_with_taxes(), 
            #'PAYMENTREQUEST_0_TAXAMT': "%0.2f" % cart.taxes(),
            #'PAYMENTREQUEST_n_SHIPPINGAMT': "%0.2f" % cart.shipping_charge(),
            #'PAYMENTREQUEST_0_ITEMAMT': "%0.2f" % cart.total(),
            'PAYMENTREQUEST_0_CURRENCYCODE': Preference.get_preference(shop).checkout_currency,
            'PAYMENTREQUEST_0_NOTIFYURL': request.build_absolute_uri(reverse("payments_paypal_ipn")),
            'SUBJECT': paypal_settings.email
        }
        success = paypal_gw.DoExpressCheckoutPayment(payment_request, paypaltoken.token, payerid)
        
        
        if success:
            #Close and clean the cart
            sell = cart.close("PayPal")
            #Set the sell payments as paid
            sell.payment.pay()
            paypaltoken.confirmed = True
            paypaltoken.save()
            
            # {'PAYMENTINFO_0_TRANSACTIONTYPE': 'expresscheckout', 'ACK': 'Success', 'PAYMENTINFO_0_PAYMENTTYPE': 'instant', 'PAYMENTINFO_0_REASONCODE': 'None', 'SHIPPINGOPTIONISDEFAULT': 'false', 'INSURANCEOPTIONSELECTED': 'false', 'CORRELATIONID': '8d20dfd3e3575', 'PAYMENTINFO_0_TAXAMT': '0.00', 'PAYMENTINFO_0_TRANSACTIONID': '6MH53467HE876651A', 'PAYMENTINFO_0_PENDINGREASON': 'None', 'PAYMENTINFO_0_AMT': '57.00', 'PAYMENTINFO_0_PROTECTIONELIGIBILITY': 'Ineligible', 'PAYMENTINFO_0_ERRORCODE': '0', 'TOKEN': 'EC-7MR99474WD5992801', 'VERSION': '63.0', 'SUCCESSPAGEREDIRECTREQUESTED': 'false', 'BUILD': '1482946', 'PAYMENTINFO_0_CURRENCYCODE': 'USD', 'PAYMENTINFO_0_FEEAMT': '1.95', 'TIMESTAMP': '2010-09-08T18:03:24Z', 'PAYMENTINFO_0_ACK': 'Success', 'PAYMENTINFO_0_ORDERTIME': '2010-09-08T18:03:23Z', 'PAYMENTINFO_0_PAYMENTSTATUS': 'Completed'}
            txn_id = paypal_gw.api_response['PAYMENTINFO_0_TRANSACTIONID']
            
            transaction = PayPalTransaction()
            transaction.transaction_id = txn_id
            transaction.sell = sell
            transaction.save()
            
            return HttpResponseRedirect(reverse('payments_success'))
        else:
            request.flash['message'] = unicode(_("Payment Failed!"))
            request.flash['severity'] = "error"
            return HttpResponseRedirect(reverse('my_shopping'))
    else:
        paypaltoken.delete()
        request.flash['message'] = unicode(_("Payment cancel!"))
        request.flash['severity'] = "notice"
        return HttpResponseRedirect(reverse('my_shopping'))


@shop_required
def paynow(request):
    from payments.models import  PayPalShopSettings, PayPalToken
    from preferences.models import Preference
        
    shop = request.shop
    cart = request.cart
    
    try:   
        paypal_settings = PayPalShopSettings.objects.filter(shop = shop).get()
    except PayPalShopSettings.DoesNotExist:
        #TODO: erase after demo!!!!
        request.flash['message'] = unicode(_("Payment failed, try other method."))
        request.flash['severity'] = "error"
        return HttpResponseRedirect(reverse('my_shopping'))
    
    total_amount = "%0.2f" % cart.total_with_taxes()
    
    return_url = request.build_absolute_uri(reverse("paypal_success"))
    cancel_url = request.build_absolute_uri(reverse("paypal_cancel"))
    
    ppgw = PayPalGateway(username=settings.PAYPAL_USERNAME,
                         password=settings.PAYPAL_PASSWORD,
                         sign=settings.PAYPAL_SIGNATURE,
                         debug=settings.PAYPAL_DEBUG)
    

    payment_request = {
        'PAYMENTREQUEST_0_PAYMENTACTION': 'Sale',
        'PAYMENTREQUEST_0_AMT': "%0.2f" % cart.total_with_taxes(),
        #'PAYMENTREQUEST_0_TAXAMT': "%0.2f" % cart.taxes(),
        #'PAYMENTREQUEST_n_SHIPPINGAMT': "%0.2f" % cart.shipping_charge(),
        #'PAYMENTREQUEST_0_ITEMAMT': "%0.2f" % cart.total(),
        'PAYMENTREQUEST_0_CURRENCYCODE': Preference.get_preference(shop).checkout_currency,
        'PAYMENTREQUEST_0_NOTIFYURL': request.build_absolute_uri(reverse("payments_paypal_ipn")),
        'SUBJECT': paypal_settings.email
    }
    
    #for i, cart_item in enumerate(cart.cartitem_set.all()):
    #    payment_request['L_PAYMENTREQUEST_0_NAME%d' % i] = cart_item.product.title.title() 
    #    payment_request['L_PAYMENTREQUEST_0_AMT%d' % i] = "%0.2f" % cart_item.product.price
    #    payment_request['L_PAYMENTREQUEST_0_QTY%d' % i] = cart_item.qty

    success = ppgw.SetExpressCheckout(payment_request, return_url, cancel_url)
    if success:
        PayPalToken(cart=cart, token=ppgw.token).save()
        return HttpResponseRedirect(ppgw.paypal_url())
    
    request.flash['message'] = unicode(_("Payment failed, try other method."))
    request.flash['severity'] = "error"
    return HttpResponseRedirect(reverse('my_shopping'))

def ipn(request):
    import logging
    logging.info(request.GET)
    logging.info(request.POST)
    return HttpResponse("")