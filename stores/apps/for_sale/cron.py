from django_cron import CronJobBase, Schedule
from for_sale.models import Item


class ShowItemsCronJob(CronJobBase):
    """ Set the show attr in the for sale items.
        If the product was sold more than two weeks ago and the quantity is cero, it can't be showing """
    
    RUN_EVERY_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'for_sale.show_items_cron_job'

    def do(self):
        for item in Item.objects.filter(qty=0, show=True):
            item.update_show(save=True)
