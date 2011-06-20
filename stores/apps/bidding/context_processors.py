# -*- coding: utf-8 -*-
from bidding.forms import BiddingSearchForm


def search(request):
    """
    This context processor provides a search form
    available in every shop page
    """
    
    if request.GET.get('q'):
        form = BiddingSearchForm(request.GET)
    else:
        form = BiddingSearchForm()

    return {"search_form": form}
