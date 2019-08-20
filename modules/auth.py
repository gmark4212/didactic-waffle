#!/usr/bin/python
# -*- coding: utf-8 -*-


class User:
    def __init__(self, db_user):
        self.active = db_user['active']
        self.email = db_user['email']
        self.name = db_user['name']
        self.stripe_id = db_user.get('stripe_id', '')

    def is_authenticated(self):
        return True

    def is_active(self):
        return self.active

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email
