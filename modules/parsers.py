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

    def get_ids(self, params, ids_root):
        ids = ()
        response = requests.get(url=self.api_root, params=params, headers=self.headers)
        if response.status_code == 200:
            ids = tuple(x['id'] for x in response.json()[ids_root])
        return ids

    def get_vacs_by_ids(self, ids):
        vacs = []
        if ids:
            for vac_id in ids:
                response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                if response.status_code == 200:
                    vacancy = response.json()
                    vacs.append(vacancy)
        return tuple(vacs)

    def process_vacancies(self, fields, vacs):
        if vacs:
            for vacancy in vacs:
                # _id = self.prefix + str(vacancy[fields['id']])
                _id = self.__class__.id + str(vacancy[fields['id']])

                if not bool(self.db.get_docs(DEF_COL, {'_id': _id}, 1)):
                    desc = self.extractor.strip_html_tags(vacancy[fields['desc']])
                    extracted_skills = self.extractor.extract_skills(desc)

                    if 'skills' in fields and vacancy[fields['skills']]:
                        key_skills = [x['name'] for x in vacancy[fields['skills']]]
                        key_skills = self.extractor.purge_cyrrilic_skills(key_skills)
                        if key_skills:
                            extracted_skills.extend(key_skills)

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

    def fetch_vacancies_portion(self, page_num):
        params = {
            'specialization': 1,
            'per_page': 100,
            'page': page_num,
        }
        fields = {
            'id': 'id',
            'desc': 'description',
            'name': 'name',
            'pub_date': 'published_at',
            'url': 'url',
            'skills': 'key_skills',
        }
        ids = self.get_ids(params, ids_root='items')
        vacs = self.get_vacs_by_ids(ids)
        self.process_vacancies(fields, vacs)


class GitHubParser(BaseParser):
    id = 'gh'

    def __init__(self):
        self.api_root = 'https://jobs.github.com/positions.json'
        super().__init__()

    def fetch_vacancies_portion(self, page_num):
        params = dict(
            page=page_num,
        )
        response = requests.get(url=self.api_root, params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                for vacancy in data:
                    vac_id = vacancy['id']
                    if not bool(self.db.get_docs(DEF_COL, {'_id': vac_id}, 1)):
                        # TODO: make skills extracting from description
                        desc = self.extractor.strip_html_tags(vacancy['description'])
                        key_skills = self.extractor.extract_skills(desc)
                        if key_skills:
                            document = {
                                '_id': vac_id,
                                'name': vacancy['title'],
                                'description': desc,
                                'pub_date': vacancy['created_at'],
                                'url': vacancy['url'],
                                'key_skills': key_skills,
                            }
                            self.db.add_doc(DEF_COL, document)
                            print(document)
        else:
            return False


class AuthenticJobsParser(BaseParser):
    id = 'authenticjobs'

    def __init__(self):
        self.api_root = 'https://authenticjobs.com/api/'
        self.__api_key = '992cbc1f22ef453412177e0aa22ed7f2'
        self.prefix = 'aj'
        super().__init__()

    def fetch_vacancies_portion(self, page_num):
        params = dict(
            api_key=self.__api_key,
            page=page_num,
            perpage=100,
            method='aj.jobs.search',
            format='json',
        )
        response = requests.get(url=self.api_root, params=params, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                data = data['listings']['listing']
                for vacancy in data:
                    vac_id = self.prefix + vacancy['id']
                    if not bool(self.db.get_docs(DEF_COL, {'_id': vac_id}, 1)):
                        desc = self.extractor.strip_html_tags(vacancy['description'])
                        key_skills = self.extractor.extract_skills(desc)
                        if key_skills:
                            document = {
                                '_id': vac_id,
                                'name': vacancy['title'],
                                'description': desc,
                                'pub_date': vacancy['post_date'],
                                'url': vacancy['url'],
                                'key_skills': key_skills,
                            }
                            self.db.add_doc(DEF_COL, document)
                            print(document)
        else:
            return False


class TheMuseParser(BaseParser):
    id = 'themuse'

    def __init__(self):
        self.api_root = 'https://www.themuse.com/api/public/jobs'
        self.__api_key = 'c86b7455e1c238124478b5cf8194435371cb55ef3523da42d0396005b2f97af7'
        self.prefix = 'ms'
        super().__init__()

    def fetch_vacancies_portion(self, page_num):
        params = dict(
            page=page_num,
        )
        response = requests.get(
            url=f'{self.api_root}?category=Data%20Science&category=Engineering',
            params=params,
            headers=self.headers
        )
        if response.status_code == 200:
            ids = tuple(x['id'] for x in response.json()['results'])
            if ids:
                for vac_id in ids:
                    response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                    if response.status_code == 200:
                        vacancy = response.json()
                        _id = self.prefix + str(vac_id)
                        if not bool(self.db.get_docs(DEF_COL, {'_id': _id}, 1)):
                            desc = self.extractor.strip_html_tags(vacancy['contents'])
                            key_skills = self.extractor.extract_skills(desc)
                            if key_skills:
                                document = {
                                    '_id': _id,
                                    'name': vacancy['name'],
                                    'description': desc,
                                    'pub_date': vacancy['publication_date'],
                                    'url': vacancy['refs']['landing_page'],
                                    'key_skills': key_skills,
                                }
                                self.db.add_doc(DEF_COL, document)


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
if __name__ == '__main__':
    f = ParserFabric()
    print(f.spawn('hh').fetch_vacancies_portion(2))
    # print(f.spawn('authenticjobs').fetch_vacancies_portion(2))
    # print(f.spawn('github').fetch_vacancies_portion(5))
    # print(f.spawn('themuse').fetch_vacancies_portion(3))
# # ----- FOR TEST USE ONLY! -----
