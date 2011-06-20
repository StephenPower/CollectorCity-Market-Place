import logging

from django.core.management.base import BaseCommand, CommandError

import httplib2

from for_sale.models import ImageItemURLQueue



class Command(BaseCommand):
    args = '<poll_id poll_id ...>'
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        
        for queued_image in ImageItemURLQueue.objects.all():
            
            try:
                queued_image.get_image()
            except httplib2.HttpLib2Error:
                logging.exception("Error fetching import image %d" % queued_image.id)
            except:
                logging.exception("Error fetching import images")
                raise
