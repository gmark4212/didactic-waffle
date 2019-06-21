#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from abc import ABC, abstractmethod
from modules.settings import *
from modules.storage import DataStorage
from modules.extractor import Extractor


class BaseParser(ABC):
    def __init__(self):
        self.db = DataStorage()
        self.extractor = Extractor(db=self.db)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) ',
        }

    @abstractmethod
    def fetch_vacancies_portion(self, page_num):
        pass

# TODO: make code DRY-ing!


class HhParser(BaseParser):
    id = 'hh'

    def __init__(self):
        self.api_root = 'https://api.hh.ru/vacancies'
        self.headers = {
            'User-Agent': 'api-test-agent',
        }
        super().__init__()

    def fetch_vacancies_portion(self, page_num):
        params = dict(
            specialization=1,
            per_page=100,
            page=page_num,
        )
        response = requests.get(url=self.api_root, params=params, headers=self.headers)
        if response.status_code == 200:
            ids = [x['id'] for x in response.json()['items']]
            if ids:
                for vac_id in ids:
                    response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                    if response.status_code == 200:
                        vacancy = response.json()

                        desc = self.extractor.strip_html_tags(vacancy['description'])
                        extracted_skills = self.extractor.extract_skills(desc)

                        if (extracted_skills or vacancy['key_skills']) and not bool(self.db.get_docs(DEF_COL, {'_id': vac_id}, 1)):
                            key_skills = [x['name'] for x in vacancy['key_skills']]
                            key_skills.extend(extracted_skills)
                            key_skills = self.extractor.purge_cyrrilic_skills(key_skills)

                            self.db.add_skill_to_ref(key_skills)

                            document = {
                                '_id': vac_id,
                                'name': vacancy['name'],
                                'description': desc,
                                'pub_date': vacancy['published_at'],
                                'url': vacancy['alternate_url'],
                                'key_skills': key_skills,
                                'salary': vacancy['salary']
                            }
                            self.db.add_doc(DEF_COL, document)
                            print(document)
            else:
                return False


class GitHubParser(BaseParser):
    id = 'github'

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


class ParserFabric:
    def __init__(self):
        self.parsers = {
            HhParser.id: HhParser,
            GitHubParser.id: GitHubParser,
            AuthenticJobsParser.id: AuthenticJobsParser,
        }

    @property
    def parsers_ids(self):
        return tuple(self.parsers.keys())

    def spawn(self, name):
        return self.parsers[name]()


# # ----- FOR TEST USE ONLY! -----
if __name__ == '__main__':
    f = ParserFabric()
    # print(f.spawn('hh').fetch_vacancies_portion(5))
    # print(f.spawn('authenticjobs').fetch_vacancies_portion(2))
    print(f.spawn('github').fetch_vacancies_portion(5))
# # ----- FOR TEST USE ONLY! -----
