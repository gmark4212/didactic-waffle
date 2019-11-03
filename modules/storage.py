#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from builtins import print
from collections.abc import Iterable, Iterator
from pymongo import MongoClient
from typing import Any, List
from settings import *


class DataStorage:
    """Class for storing and processing data in a non-relational database.

    Attributes:
        client: pointer to client-side representation of a MongoDB cluster
        db: database connection
        docs_map: memory cache to speed up data acquisition
    """

    def __init__(self):
        try:
            self.client = MongoClient(f'{DEFAULT_HOST}:{MONGODB_PORT}')
            self.db = self.client[MONGO_DB_NAME]
        except Exception as e:
            print(f'ERROR: {str(e)}')
        self.docs_map = {}

    def get_docs(self, collection_name=None, _filter={}, limit=None, _sort_field='_id'):
        """Retrieves documents from a specific collection. Supports filtering and limiting.
        Parameters:
            collection_name: str
                the name of the collection in the database
            _filter: dict
                filtration conditions
                https://docs.mongodb.com/manual/reference/operator/aggregation/filter/
            limit: int
                limit the number of documents returned
                https://docs.mongodb.com/manual/reference/operator/aggregation/limit/
            _sort_field: str
                sort field
                https://docs.mongodb.com/manual/reference/operator/aggregation/sort/
        """

        if self.__is_valid(collection_name):
            if limit:
                return [i for i in self.db[collection_name].find(_filter).limit(limit).sort(_sort_field)]
            else:
                return [i for i in self.db[collection_name].find(_filter).sort(_sort_field)]

    def get_doc_by_id(self, collection_name=None, key=None):
        """Finds the document in the collection by id.
        If the document is in the cache it returns from the cache"""

        if key:
            return self.docs_map.get(
                self.docs_map[key],
                self.db.get_docs(collection_name, {'_id': key}, 1)
            )

    def add_doc(self, collection_name=None, data=None):
        """Adds the document to collection (with caching)"""

        if self.__is_valid(collection_name) and isinstance(data, dict):
            if '_id' in data and data['_id'] not in self.docs_map.keys():
                self.docs_map[data['_id']] = data
            print('+', data)
            self.db[collection_name].insert_one(data)

    def delete_docs(self, _filter=None, collection_name=None):
        """Deletes documents from the collection according to the specified filter"""

        if _filter and isinstance(_filter, dict) and collection_name:
            self.db[collection_name].delete_many(_filter)

    def update_doc(self, collection_name=None, _filter=None, set_dict=None):
        """Updates documents found by the filter with the specified data."""

        if self.__is_valid(collection_name) \
                and _filter and isinstance(_filter, dict) \
                and set_dict and isinstance(set_dict, dict):
            self.db[collection_name].update_one(_filter, {"$set": set_dict}, upsert=False)

    def __is_valid(self, collection_name):
        """Checks for a collection in the database."""

        return bool(collection_name) and hasattr(self.db, collection_name)

    def add_skill_to_ref(self, skills):
        if isinstance(skills, str):
            x = list()
            x.append(skills)
            skills = x
        elif isinstance(skills, list):
            skills = list(set(skills))
        elif isinstance(skills, dict):
            low = skills['low']
            exist_in_ref = self.get_docs(SKILLS_REF, {'low': low}, 1)
            if not exist_in_ref:
                self.add_doc(SKILLS_REF, skills)
            else:
                for existing in exist_in_ref:
                    if 'desc' not in existing:
                        self.delete_docs(_filter={'low': low}, collection_name=SKILLS_REF)
                        self.add_doc(SKILLS_REF, skills)
            return

        for skill in skills:
            if isinstance(skill, str):
                lower_cased_skill = skill.lower()
                exist_in_ref = self.get_docs(SKILLS_REF, {'low': lower_cased_skill}, 1)
                if not exist_in_ref:
                    self.add_doc(SKILLS_REF, {'name': skill, 'low': lower_cased_skill})

    def get_key_skills_ref(self):
        ref = self.get_docs(SKILLS_REF)
        return tuple(x['name'] for x in ref)

    def get_paid_vacancies(self):
        return self.get_docs(DEF_COL, _filter={'salary.from': {'$gt': 0}}, limit=100, _sort_field='salary.from')

    @staticmethod
    def __create_search_pattern(search_str):
        keywords = set(search_str.split())
        if len(keywords) > 1:
            pattern = '^'.join(r'(?=.*\b' + re.escape(x) + r'\b)' for x in keywords) + r'.*$'
        else:
            pattern = r'\b' + re.escape(list(keywords)[0]) + r'\b'
        return pattern

    def fetch_top_skills(self, search_str, vacs_limit=0, no_vacs=False, is_russia=True):
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
        coll = self.db[DEF_COL]
        data = list(coll.aggregate(pipeline))

        top = {
            'data': data,
            'labels': [x['_id'] for x in data],
            'freqs': [x['frequency'] for x in data],
        }

        if not no_vacs:
            for i in top['data']:
                i['vacs'] = self.get_vacancies_by_skill(i['_id'], search_str, vacs_limit, is_russia=is_russia)
                i['visible'] = False

        return top

    def get_vacancies_by_skill(self, skill, search_str='', limit=0, is_russia=True):
        pipeline = []

        if search_str:
            pipeline.append(
                {"$match": {"name": {"$regex": self.__create_search_pattern(search_str), "$options": "gi"}}}
            )

        pipeline.extend([
            {"$unwind": "$key_skills"},
            {"$match": {"key_skills": {"$regex": skill, "$options": "gi"}}},
            {"$sort": {"pub_date": -1}}
        ])

        if not is_russia:
            pipeline[2]["$match"]["_id"] = {"$regex": r"^(?!hh).+", "$options": "gi"}

        if limit > 0:
            pipeline.append(
                {"$limit": limit}
            )

        coll = self.db[DEF_COL]
        vacs = list(coll.aggregate(pipeline))
        vacs = [{'name': x['name'], 'url': x['url'], 'pub_date': x['pub_date']} for x in vacs]
        # clean duplicates
        return [dict(t) for t in {tuple(d.items()) for d in vacs}]

    def get_skills_ref(self):
        skills = list(self.get_docs(SKILLS_REF))
        return [{'name': x['name'], '_id': str(x['_id'])} for x in skills]

    def get_skill_details(self, top_skills):
        for i in top_skills['data']:
            i['ads'] = self.get_ads_by_skill(i['_id'])
            s = self.get_docs(SKILLS_REF, _filter={'low': i['_id'].lower()}, limit=1)
            if s:
                s = s[0]
                if 'desc' in s:
                    i['desc'] = s['desc']
                    i['ctg'] = s['ctg']
                    i['logo'] = s['logo']
                    i['site'] = s['site']

    def get_ads_by_skill(self, skill=None, limit=0):
        if skill:
            pipeline = [
                {"$match": {"paid": True}},
                {"$unwind": "$campaign"},
                {"$unwind": "$campaign.skills"},
                {"$match": {"campaign.skills": {"$regex": skill, "$options": "gi"}}},
                {"$project": {"_id": 0, "campaign": 1}}
            ]

            if limit > 0:
                pipeline.append(
                    {"$limit": limit}
                )

            collection = self.db[ADS_COL]
            ads = list(collection.aggregate(pipeline))
            return ads
        return None


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
