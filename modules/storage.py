#!/usr/bin/python
# -*- coding: utf-8 -*-
from pymongo import MongoClient
from modules.settings import *
from modules.extractor import ExtractorFacade


class DataStorage:
    def __init__(self, ef=None):
        if ef:
            self.ef = ef
        else:
            self.ef = ExtractorFacade()

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

    def add_skill_to_ref(self, skills):
        if isinstance(skills, str):
            x = list()
            x.append(skills)
            skills = x

        for skill in skills:
            exist_in_ref = self.get_docs(SKILLS_REF, {'name': skill}, 1)
            if not exist_in_ref:
                self.add_doc(SKILLS_REF, {'name': skill})

    def fetch_top_skills(self, search_str):
        keywords = search_str.split()
        extra_keywords = []
        for i in keywords:
            synonyms = self.ef.check_synonyms(i)
            if synonyms:
                extra_keywords.extend(synonyms)

        if extra_keywords:
            keywords.extend(extra_keywords)

        keywords = set(keywords)
        if len(keywords) > 1:
            s = ''.join(f'{x}|' for x in keywords)
            s = s[:len(s) - 1]
            pattern = f'({s}).*?({s})'
        else:
            pattern = list(keywords)[0]

        pipeline = [
            {"$match": {"name": {"$regex": pattern, "$options": "gi"}}},
            {"$unwind": "$key_skills"},
            {"$group": {
                "_id": "$key_skills",
                "frequency": {"$sum": 1}
            }},
            {"$sort": {"frequency": -1}},
            {"$limit": SKILLS_LIMIT}
        ]

        col = self.db[DEF_COL]

        return list(col.aggregate(pipeline))
