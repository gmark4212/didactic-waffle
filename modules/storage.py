#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from modules.settings import *


class DataStorage:
    def __init__(self):
        try:
            self.client = MongoClient(f'{DEFAULT_HOST}:{MONGODB_PORT}')
            self.db = self.client[MONGO_DB_NAME]
        except Exception as e:
            print(f'ERROR: {str(e)}')

    def get_docs(self, collection_name=None, _filter={}, limit=None):
        if self.__is_valid(collection_name):
            if limit:
                return [i for i in self.db[collection_name].find(_filter).limit(limit)]
            else:
                return [i for i in self.db[collection_name].find(_filter)]

    def add_doc(self, collection_name=None, data=None):
        if self.__is_valid(collection_name) and isinstance(data, dict):
            self.db[collection_name].insert_one(data)

    def __is_valid(self, collection_name):
        return bool(collection_name) and hasattr(self.db, collection_name)

