#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import re


class BaseParser:
    def __init__(self):
        self.TAG_RE = re.compile(r'<[^>]+>')

    def strip_html_tags(self, text):
        return self.TAG_RE.sub('', text)


class HhParser(BaseParser):
    def __init__(self):
        self.api_root = 'https://api.hh.ru/vacancies'
        self.headers = {
            'User-Agent': 'api-test-agent',
        }
        super().__init__()

    def _fetch_vacancies_portion(self, page_num=1):
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
                        name = vacancy['name']
                        descr = self.strip_html_tags(vacancy['description'])
                        pub_date = vacancy['published_at']
                        url = vacancy['alternate_url']

                        if vacancy['key_skills']:
                            key_skills = [x['name'] for x in vacancy['key_skills']]
                            print(vac_id, key_skills, name, pub_date, url)
            else:
                return False

    def fetch_last_vacancies(self):
        for i in range(20):
            ok = self._fetch_vacancies_portion(i)
            if ok is False:
                break


class GitHubParser(BaseParser):
    def __init__(self):
        self.api_root = 'https://jobs.github.com/positions.json'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/69.0.3497.105 Mobile/15E148 Safari/605.1',
        }
        super().__init__()


h = HhParser()
h.fetch_last_vacancies()
