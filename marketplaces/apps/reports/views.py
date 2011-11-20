import logging
import datetime
import decimal

from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

def get_daily_activity_data(day):
    from market.models import MarketPlace
    from shops.models import Shop
    from subscriptions.models import SubscriptionCancelation
            
    month_init = datetime.datetime(day.year, day.month, 1, 0, 0, 0)
    if day.month == 12:
        month_end = datetime.datetime(day.year + 1, 1, 1, 0, 0, 0)
    else:
        month_end = datetime.datetime(day.year, day.month + 1, 1, 0, 0, 0)
    day_init = datetime.datetime(day.year, day.month, day.day, 0, 0, 0)
    day_end = datetime.datetime(day.year, day.month, day.day, 23, 59, 59)
    
    params = {}
    try:
        params['day'] = day
        params['month_init'] = month_init
        params['month_end'] = month_end
        
        total_customers = 0
        total_signups_today = 0
        total_signups_this_month = 0
        total_cancelations_today = 0
        total_cancelations_this_month = 0
        marketplaces = MarketPlace.objects.all()
        
        params['columns'] = ["MarketPlace", "Customers", "Signups Today", "Signup This Month", "Cancelations Today", "Cancelation This Month", "Churn %"]
        params['rows'] = []
        
        for market in marketplaces:
            #"do calculations
            marketplace_customers = Shop.objects.filter(marketplace=market)
            marketplace_signups_today = marketplace_customers.filter(date_time__gte=day_init).filter(date_time__lte=day_end)
            marketplace_signups_this_month = marketplace_customers.filter(date_time__gte=month_init).filter(date_time__lte=month_end)
            marketplace_total_cancelations_today = SubscriptionCancelation.objects.filter(shop__in=market.shop_set.all()).filter(date_time__gte=day_init).filter(date_time__lte=day_end)
            marketplace_total_cancelations_this_month = SubscriptionCancelation.objects.filter(shop__in=market.shop_set.all()).filter(date_time__gte=month_init).filter(date_time__lte=month_end)   
            try:
                marketplace_churn_percent = "%s %%" % (round((float(marketplace_total_cancelations_this_month.count()) / float(marketplace_customers.count())) * 100, 2))
            except ZeroDivisionError:
                marketplace_churn_percent = "0 %"
            
            row = [market, marketplace_customers.count(), marketplace_signups_today.count(), marketplace_signups_this_month.count(), marketplace_total_cancelations_today.count(), marketplace_total_cancelations_this_month.count(), marketplace_churn_percent] 
            params['rows'].append(row)
            
            total_customers += marketplace_customers.count()
            total_signups_today += marketplace_signups_today.count()
            total_signups_this_month += marketplace_signups_this_month.count()
            total_cancelations_today += marketplace_total_cancelations_today.count()
            total_cancelations_this_month += marketplace_total_cancelations_this_month.count()
             
        params['totals'] = ["Totals", total_customers, total_signups_today, total_signups_this_month, total_cancelations_today, total_cancelations_this_month, "%s %%" %  (round((float(total_cancelations_this_month) / float(total_customers)) * 100, 2))]
                
    except Exception, e:
        logging.info(e)
        
    return params

    
def get_monthly_revenue_data():
    from market.models import MarketPlace
            
    day = datetime.datetime.now()
    params = {}
    try:
        params['day'] = day
        params['columns'] = ["MarketPlace", "Plan" , "# of Accounts", "Monthly Charge", "Total"]
        params['rows'] = []
        
        total_amount_of_accounts = 0
        total_revenue = 0
        total_monthly_charge = 0
        
        marketplaces = MarketPlace.objects.all()
        
        for market in marketplaces:
            for plan in market.subscriptionplan_set.all():
                
                subscriptions = plan.subscription_set.all()
                
                accounts = subscriptions.count()
                
                total_amount_of_accounts += accounts
                plan_revenue = round(accounts * decimal.Decimal(plan.price), 2)
                total_revenue += plan_revenue
                total_monthly_charge += decimal.Decimal(plan.price)
                row = [market, plan.name, accounts, "u$s %s" % decimal.Decimal(plan.price), "u$s %s" % plan_revenue]
                params['rows'].append(row)
            
        params['totals'] = ["Totals", "-", total_amount_of_accounts, "u$s %s" % total_monthly_charge, "u$s %s" % total_revenue]
        
                
    except Exception, e:
        logging.info(e)
        
    return params
    

def get_daily_transactions_data(day):
    from payments.gateways.braintreegw import BraintreeGateway
    from django.conf import settings
    
    gw = BraintreeGateway(settings.MERCHANT_ID, settings.PUBLIC_KEY, settings.PRIVATE_KEY)
    
    params = {}
    try:
        transactions = gw.get_transactions(day)    
        
        params['day'] = day
        params['columns'] = ["TransactionID", "Amount", "Website", "Email", "User"]
        
        sections = []
        for status in transactions.iterkeys():
            
            section = {}
            section['type'] = status
            
            t_list = transactions[status]
            
            section['len'] = len(t_list)
            section['txs'] = []
            
            total = 0
            for transaction in t_list:
                user_name = "- Unknown -" if transaction.customer_details.first_name is None or transaction.customer_details.last_name is None else "%s, %s" % (transaction.customer_details.last_name, transaction.customer_details.first_name)
                tx = [transaction.id, "u$s %s" % round(decimal.Decimal(transaction.amount), 2), transaction.customer_details.website, transaction.customer_details.email, user_name] 
                total += decimal.Decimal(transaction.amount)
                section['txs'].append(tx)
            section['total'] = total
            sections.append(section)            
            
        params['sections'] = sections
    
    except Exception, e:
        logging.info(e)
    
    return params

@staff_member_required
def admin_daily_activity_report(request):
    date = request.GET.get("date", None)
    if date:
        day = datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        day = datetime.datetime.today()
    params = get_daily_activity_data(day)
    return render_to_response("admin/daily_activity_report.html", params, RequestContext(request))

@staff_member_required
def admin_monthly_revenue_report(request):
    params = get_monthly_revenue_data()
    return render_to_response("admin/monthly_revenue_report.html", params, RequestContext(request))

@staff_member_required
def admin_daily_transactions_report(request):
    date = request.GET.get("date", None)
    if date:
        day = datetime.datetime.strptime(date, "%Y-%m-%d")
    else:
        day = datetime.datetime.today()
    params = get_daily_transactions_data(day)    
    return render_to_response("admin/daily_transactions_report.html", params, RequestContext(request))

@staff_member_required
def admin_reports(request):
    return render_to_response("admin/reports.html", {}, RequestContext(request))

@staff_member_required
def admin_shop_subscriptions_report(request):
    from shops.models import Shop
    shops = Shop.objects.all()
    return render_to_response("admin/shop_subscriptions_report.html", {'shops': shops}, RequestContext(request))

@staff_member_required
def admin_shop_revenue_report(request):
    from shops.models import Shop
    shops = Shop.objects.all()
    return render_to_response("admin/shop_revenue_report.html", {'shops': shops}, RequestContext(request))

@staff_member_required
def admin_shop_subscription_details(request, id):
    from shops.models import Shop
    from subscriptions.models import Subscription
    shop = get_object_or_404(Shop, pk=id)
    admin = shop.owner()
    
    try:
        subscription = Subscription.objects.filter(owner__user=admin).get()
    except Subscription.DoesNotExist:
        subscription = None
        
    return render_to_response("admin/shop_subscription.html", {'shop' : shop, 'subscription' : subscription}, RequestContext(request))

@staff_member_required
def admin_shop_abandonment_report(request):
    from shops.models import Shop
    
    filters = [
        ('no_filter', '-- No Filter --'),
        ('post_gt_30', 'Post &gt; 30 days'),
        ('post_gt_60', 'Post &gt; 60 days'),
        ('post_gt_90', 'Post &gt; 90 days'),        
        ('login_gt_30', 'Login &gt; 30 days'),
        ('login_gt_60', 'Login &gt; 60 days'),        
        ('login_gt_90', 'Login &gt; 90 days'),
    ]
    
    filter = request.GET.get("filter", None)
    shops = Shop.objects.all()
    if filter is not None or filter == '-- No Filter --':
        if filter == "login_gt_30":
            d1 = datetime.datetime.now() - datetime.timedelta(days=30)
            shops = shops.filter(admin__last_login__lt=d1)
        elif filter == "login_gt_60":
            d1 = datetime.datetime.now() - datetime.timedelta(days=60)
            shops = shops.filter(admin__last_login__lt=d1)
        elif filter == "login_gt_90":
            d1 = datetime.datetime.now() - datetime.timedelta(days=90)
            shops = shops.filter(admin__last_login__lt=d1)
        elif filter == "post_gt_30":
            d1 = datetime.datetime.now() - datetime.timedelta(days=30)
            shops = shops.filter(last_date_to_post__lt=d1)
        elif filter == "post_gt_60":
            d1 = datetime.datetime.now() - datetime.timedelta(days=60)
            shops = shops.filter(last_date_to_post__lt=d1)
        elif filter == "post_gt_90":
            d1 = datetime.datetime.now() - datetime.timedelta(days=90)
            shops = shops.filter(last_date_to_post__lt=d1)
            
    params = {'shops': shops, 'filters': filters, 'filter': filter}
    
    return render_to_response("admin/shop_abandonment_report.html", params, RequestContext(request))