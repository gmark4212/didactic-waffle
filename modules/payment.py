#!/usr/bin/python
# -*- coding: utf-8 -*-
import stripe
from modules._sensitive import STRIPE_SK


class StripePay:
    def __init__(self):
        stripe.api_key = STRIPE_SK
        self.stripe = stripe

    def get_customers(self, email=None, limit=10):
        return list(self.stripe.Customer.list(email=email, limit=limit))

    def get_customer_id(self, email=None):
        if email:
            last = self.get_customers(email=email, limit=1)
            if last:
                last = dict(last[0])
                stripe_id = last.get('id', None)
                return stripe_id


if __name__ == '__main__':
    s = StripePay()
    i = s.get_customers('gmark4212@gmail.com')
    print(i['data'])
