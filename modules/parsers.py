#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re
from modules.settings import *
from modules.storage import DataStorage


class BaseParser:
    def __init__(self):
        self.TAG_RE = re.compile(r'<[^>]+>')
        self.db = DataStorage()

    def strip_html_tags(self, text):
        return self.TAG_RE.sub('', text)


class HhParser(BaseParser):
    def __init__(self):
        self.api_root = 'https://api.hh.ru/vacancies'
        self.headers = {
            'User-Agent': 'api-test-agent',
        }
        super().__init__()

    def fetch_vacancies_portion(self, page_num):
        print(f'====================== {page_num} ==========================')

        params = dict(
            specialization=1,
            per_page=100,
            page=page_num,
        )
        response = requests.get(url=self.api_root, params=params, headers=self.headers)
        if response.status_code == 200:
            ids = [x['id'] for x in response.json()['items']]
            print(len(ids))

            if ids:
                for vac_id in ids:
                    response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                    if response.status_code == 200:
                        vacancy = response.json()

                        # process only if it has key skills and id is not in db
                        if vacancy['key_skills'] and not bool(self.db.get_docs(DEF_COL, {'_id': vac_id}, 1)):
                            key_skills = [x['name'] for x in vacancy['key_skills']]
                            document = {
                                '_id': vac_id,
                                'name': vacancy['name'],
                                'description': self.strip_html_tags(vacancy['description']),
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
    def __init__(self):
        self.api_root = 'https://jobs.github.com/positions.json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1',
        }
        super().__init__()
