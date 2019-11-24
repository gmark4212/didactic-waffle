#!/usr/bin/python
# -*- coding: utf-8 -*-
from geoip2.database import Reader
from pycountry import countries


class GetCountry:
    """Class for identify country.

    Attributes:
        ip: user IP
    """
    def __init__(self):
        self.ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        self.reader = Reader('GeoLite2-Country.mmdb')

    def get_country_from_db(self):
        """Returns the country from GeoLite2-Country.mmdb"""
        try:
            c = self.reader.country(self.ip)
            c = c.country.iso_code
            return c
        except Exception:
            return None

    @staticmethod
    def get_iso_code(country):
        """Returns ISO country code"""
        country_name = countries.get(name=country)
        country_iso = countries.get(alpha_2=country)
        country_alpha_3 = countries.get(alpha_3=country)
        if country_name is not None:
            return country_name.alpha_2
        elif country_iso is not None:
            return country_iso.alpha_2
        elif country_alpha_3 is not None:
            return country_alpha_3.alpha_2
