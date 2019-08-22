#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import stripe
from modules._sensitive import STRIPE_SK


class StripePay:
    def __init__(self):
        stripe.api_key = STRIPE_SK
        self.stripe = stripe

    def get_customers(self, email=None, limit=100):
        return list(self.stripe.Customer.list(email=email, limit=limit))

    def get_customer_ids(self, email=None, limit=1):
        ids = ()
        if email:
            customers = self.get_customers(email=email, limit=limit)
            if customers:
                for customer in customers:
                    customer = dict(customer)
                    stripe_id = customer.get('id', None)
                    ids = ids + (stripe_id,)
        return ids

    def get_customer_charges(self, customer_id=None, limit=100):
        charges_tuple = ()
        if customer_id:
            charges = list(self.stripe.Charge.list(customer=customer_id, limit=limit))
            for charge in charges:
                charge = dict(charge)
                status = charge['status']
                if status == 'succeeded':
                    created = charge['created']
                    created_dt = datetime.utcfromtimestamp(int(created)).strftime('%Y-%m-%d %H:%M:%S')
                    paid_til = created + 2592000
                    paid_til_dt = datetime.utcfromtimestamp(int(paid_til)).strftime('%Y-%m-%d %H:%M:%S')
                    charges_tuple = charges_tuple + ({
                        'created': created,
                        'created_dt': created_dt,
                        'paid_til': paid_til,
                        'paid_til_dt': paid_til_dt,
                        'amount': int(charge['amount']) / 100,
                        'paid': charge['paid'],
                        'status': status,
                    },)
        return charges_tuple

    def get_history(self, email=None, limit=100):
        charges = ()
        customer_ids = self.get_customer_ids(email, limit)
        for cid in customer_ids:
            charge = self.get_customer_charges(cid)
            charges = charges + (charge[0],)
        return charges

    def is_current_campaign_paid(self, email=None):
        is_paid = False
        charge = self.get_history(email, 1)
        if charge:
            charge = charge[0]
            paid_til = datetime.fromtimestamp(charge['paid_til'])
            is_paid = datetime.now() < paid_til
        return {'campaign_is_paid': is_paid}


# if __name__ == '__main__':
#     import pprint
#     s = StripePay()
#     i = s.is_current_campaign_paid('gmark4212@gmail.com')
#     pprint.pprint(i, width=1)

