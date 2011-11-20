from django.db import models

class FeaturesHelpText(models.Model):
    auctions = models.TextField(default="Help text description here!")
    wishlist = models.TextField(default="Help text description here!")
    mailinglist = models.TextField(default="Help text description here!")
    google_analytics = models.TextField(default="Help text description here!")
    show_attendance = models.TextField(default="Help text description here!")
    custom_dns = models.TextField(default="Help text description here!")
    paypal = models.TextField(default="Help text description here!")
    google_checkout = models.TextField(default="Help text description here!")
    credit_card = models.TextField(default="Help text description here!")
    manual_payment = models.TextField(default="Help text description here!")
    theme_change = models.TextField(default="Help text description here!")
    add_new_pages = models.TextField(default="Help text description here!")