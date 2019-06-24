#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from abc import ABC, abstractmethod
from functools import reduce
import operator
from modules.settings import *
from modules.storage import DataStorage
from modules.extractor import Extractor


class BaseParser(ABC):
    id = None

    def __init__(self):
        self.api_root = None
        self.fields = None
        self.db = DataStorage()
        self.extractor = Extractor(db=self.db)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) ',
        }

    @abstractmethod
    def fetch_vacancies_portion(self, page_num):
        pass

    @staticmethod
    def get_field_from_nested_dict(data_dict, map_tuple):
        return reduce(operator.getitem, map_tuple, data_dict)

    def get_ids(self, params, ids_root, str_get_params=''):
        ids = ()
        response = requests.get(url=self.api_root + str_get_params, params=params, headers=self.headers)
        if response.status_code == 200:
            ids = tuple(x['id'] for x in response.json()[ids_root])
        return ids

    def get_vacs_by_ids(self, ids=None):
        vacs = []
        if ids:
            for vac_id in ids:
                response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                if response.status_code == 200:
                    vacancy = response.json()
                    vacs.append(vacancy)
        return tuple(vacs)

    def get_vacs_by_root(self, params, data_map=None):
        vacs = []
        response = requests.get(self.api_root, params=params, headers=self.headers)
        data = response.json()
        if isinstance(data_map, tuple):
            data = self.get_field_from_nested_dict(data, data_map)
        if data:
            for vacancy in data:
                vacs.append(vacancy)
        return tuple(vacs)

    def process_vacancies(self, vacs):
        if vacs:
            fields = self.fields
            for vacancy in vacs:
                _id = self.__class__.id + str(vacancy[fields['id']])

                if not bool(self.db.get_docs(DEF_COL, {'_id': _id}, 1)):
                    desc = self.extractor.strip_html_tags(vacancy[fields['desc']])
                    extracted_skills = self.extractor.extract_skills(desc)

                    if 'skills' in fields and vacancy[fields['skills']]:
                        key_skills = [x['name'] for x in vacancy[fields['skills']]]
                        key_skills = self.extractor.purge_cyrrilic_skills(key_skills)
                        if key_skills:
                            extracted_skills.extend(key_skills)
                            extracted_skills = list(set(extracted_skills))

                    if extracted_skills:
                        url_map = fields['url']
                        if isinstance(url_map, tuple):
                            vacancy_url = self.get_field_from_nested_dict(vacancy, url_map)
                        else:
                            vacancy_url = url_map

                        document = {
                            '_id': _id,
                            'name': vacancy[fields['name']],
                            'description': desc,
                            'pub_date': vacancy[fields['pub_date']],
                            'url': vacancy_url,
                            'key_skills': extracted_skills,
                        }

                        self.db.add_doc(DEF_COL, document)


class HhParser(BaseParser):
    id = 'hh'

    def __init__(self):
        super().__init__()
        self.api_root = 'https://api.hh.ru/vacancies'
        self.headers = {
            'User-Agent': 'api-test-agent',
        }
        self.fields = {
            'id': 'id',
            'desc': 'description',
            'name': 'name',
            'pub_date': 'published_at',
            'url': 'url',
            'skills': 'key_skills',
        }

    def fetch_vacancies_portion(self, page_num):
        params = {
            'specialization': 1,
            'per_page': 100,
            'page': page_num,
        }
        ids = self.get_ids(params, ids_root='items')
        vacs = self.get_vacs_by_ids(ids)
        self.process_vacancies(vacs)


class GitHubParser(BaseParser):
    id = 'gh'

    def __init__(self):
        super().__init__()
        self.api_root = 'https://jobs.github.com/positions.json'
        self.fields = {
            'id': 'id',
            'desc': 'description',
            'name': 'title',
            'pub_date': 'created_at',
            'url': 'url',
        }

    def fetch_vacancies_portion(self, page_num):
        params = {
            'page': page_num,
        }
        vacs = self.get_vacs_by_root(params)
        self.process_vacancies(vacs)


class AuthenticJobsParser(BaseParser):
    id = 'aj'

    def __init__(self):
        super().__init__()
        self.api_root = 'https://authenticjobs.com/api/'
        self.fields = {
            'id': 'id',
            'desc': 'description',
            'name': 'title',
            'pub_date': 'post_date',
            'url': 'url',
        }

    def fetch_vacancies_portion(self, page_num):
        params = {
            'api_key': '992cbc1f22ef453412177e0aa22ed7f2',
            'page': page_num,
            'perpage': 100,
            'method': 'aj.jobs.search',
            'format': 'json',
        }
        vacs = self.get_vacs_by_root(params, data_map=('listings', 'listing'))
        self.process_vacancies(vacs)


class TheMuseParser(BaseParser):
    id = 'ms'

    def __init__(self):
        super().__init__()
        self.api_root = 'https://www.themuse.com/api/public/jobs'
        self.fields = {
            'id': 'id',
            'desc': 'contents',
            'name': 'name',
            'pub_date': 'publication_date',
            'url': ('refs', 'landing_page'),
        }

    def fetch_vacancies_portion(self, page_num):
        params = {
            'page': page_num,
            'api-key': 'c86b7455e1c238124478b5cf8194435371cb55ef3523da42d0396005b2f97af7',
        }
        ids = self.get_ids(params, ids_root='results', str_get_params='?category=Data%20Science&category=Engineering')
        vacs = self.get_vacs_by_ids(ids)
        self.process_vacancies(vacs)


class ParserFabric:
    def __init__(self):
        self.parsers = {
            HhParser.id: HhParser,
            GitHubParser.id: GitHubParser,
            AuthenticJobsParser.id: AuthenticJobsParser,
            TheMuseParser.id: TheMuseParser,
        }

    @property
    def parsers_ids(self):
        return tuple(self.parsers.keys())

    def spawn(self, name):
        return self.parsers[name]()


# # ----- FOR TEST USE ONLY! -----
# if __name__ == '__main__':
#     f = ParserFabric()
    # print(f.spawn('hh').fetch_vacancies_portion(2))
    # print(f.spawn('aj').fetch_vacancies_portion(1))
    # print(f.spawn('gh').fetch_vacancies_portion(1))
    # print(f.spawn('ms').fetch_vacancies_portion(4))
# # ----- FOR TEST USE ONLY! -----
