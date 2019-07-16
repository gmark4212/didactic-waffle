#!/usr/bin/python
# -*- coding: utf-8 -*-


class User:
    def __init__(self, db_user):
        self.email = db_user['email']
        self.name = db_user['name']

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.email
