#!/usr/bin/python
# -*- coding: utf-8 -*-
from builtins import print
from pymongo import MongoClient
from collections.abc import Iterable, Iterator
from typing import Any, List
from modules.settings import *


class DataStorage:

    def __init__(self):
        try:
            self.client = MongoClient(f'{DEFAULT_HOST}:{MONGODB_PORT}')
            self.db = self.client[MONGO_DB_NAME]
        except Exception as e:
            print(f'ERROR: {str(e)}')
        self.docs_map = {}

    def get_docs(self, collection_name=None, _filter={}, limit=None, _sort_field='_id'):
        if self.__is_valid(collection_name):
            if limit:
                return [i for i in self.db[collection_name].find(_filter).limit(limit).sort(_sort_field)]
            else:
                return [i for i in self.db[collection_name].find(_filter).sort(_sort_field)]

    def get_doc_by_id(self, collection_name=None, key=None):
        if key:
            if key in self.docs_map.keys():
                return self.docs_map[key]
            else:
                return self.db.get_docs(collection_name, {'_id': key}, 1)

    def add_doc(self, collection_name=None, data=None):
        if self.__is_valid(collection_name) and isinstance(data, dict):
            if '_id' in data and data['_id'] not in self.docs_map.keys():
                self.docs_map[data['_id']] = data
                print('+', self.docs_map)
            self.db[collection_name].insert_one(data)

    def __is_valid(self, collection_name):
        return bool(collection_name) and hasattr(self.db, collection_name)

    def add_skill_to_ref(self, skills):
        if isinstance(skills, str):
            x = list()
            x.append(skills)
            skills = x
        else:
            skills = list(set(skills))

        for skill in skills:
            exist_in_ref = self.get_docs(SKILLS_REF, {'name': skill}, 1)
            if not exist_in_ref:
                self.add_doc(SKILLS_REF, {'name': skill})

    def get_key_skills_ref(self):
        ref = self.get_docs(SKILLS_REF)
        return tuple(x['name'] for x in ref)

    def get_paid_vacancies(self):
        return self.get_docs(DEF_COL, _filter={'salary.from': {'$gt': 0}}, limit=100, _sort_field='salary.from')

    @staticmethod
    def __create_search_pattern(search_str):
        keywords = search_str.split()
        keywords = set(keywords)
        if len(keywords) > 1:
            s = ''.join(f'{x}|' for x in keywords)
            s = s[:len(s) - 1]
            pattern = f'({s}).*?({s})'
        else:
            pattern = list(keywords)[0]
        return pattern

    def fetch_top_skills(self, search_str):
        pipeline = [
            {"$match": {"name": {"$regex": self.__create_search_pattern(search_str), "$options": "gi"}}},
            {"$unwind": "$key_skills"},
            {"$group": {
                "_id": "$key_skills",
                "frequency": {"$sum": 1}
            }},
            {"$sort": {"frequency": -1}},
            {"$limit": SKILLS_LIMIT}
        ]
        col = self.db[DEF_COL]
        top = list(col.aggregate(pipeline))
        for i in top:
            i['vacs'] = self.get_vacancies_by_skill(i['_id'], search_str)
            i['visible'] = False
        return top

    def get_vacancies_by_skill(self, skill, search_str):
        pipeline = [
            {"$match": {"name": {"$regex": self.__create_search_pattern(search_str), "$options": "gi"}}},
            {"$unwind": "$key_skills"},
            {"$match": {"key_skills": skill}},
            {"$sort": {"pub_date": -1}}
        ]
        col = self.db[DEF_COL]
        vacs = list(col.aggregate(pipeline))
        return [{'name': x['name'], 'url': x['url']} for x in vacs]


#  ++++++++++++++++ Iterator pattern example ++++++++++++++++
class SalaryVacancyIterator(Iterator):
    _position: int = None
    _reverse: bool = False

    def __init__(self, coll: [], reverse: bool = False):
        self._collection = coll
        self._reverse = reverse
        self._position = -1 if reverse else 0

    def __next__(self):
        try:
            value = self._collection[self._position]
            self._position += -1 if self._reverse else 1
        except IndexError:
            raise StopIteration()

        return value


class VacanciesCollection(Iterable):
    def __init__(self, coll: List[Any] = []):
        self._collection = coll

    def __iter__(self):
        return SalaryVacancyIterator(self._collection)

    def get_reverse_iterator(self):
        return SalaryVacancyIterator(self._collection, True)

    def add_item(self, item: Any):
        self._collection.append(item)

#  ++++++++++++++++ Iterator pattern example ++++++++++++++++
