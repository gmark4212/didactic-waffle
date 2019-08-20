#!/usr/bin/python
# -*- coding: utf-8 -*-
import stripe
from modules._sensitive import STRIPE_SK


class StripePay:
    def __init__(self):
        stripe.api_key = STRIPE_SK
        self.stripe = stripe

    def get_customers(self, email=None, limit=10):
        return self.stripe.Customer.list(email=email, limit=limit)


if __name__ == '__main__':
    s = StripePay()
    i = s.get_customers('gmark4212@gmail.com')
    print(i['data'])
