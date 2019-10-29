#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from abc import ABC, abstractmethod
from functools import reduce
import operator
from modules.settings import *
from modules.storage import DataStorage
from modules.extractor import Extractor

from user_agent import generate_user_agent
from bs4 import BeautifulSoup
import re


class BaseParser(ABC):
    """Base class for API-parsers.

    Attributes:
        id: parser instance identifier
    """

    id = None

    def __init__(self):
        """
        Attributes:
        api_root: str
            stores initial API url
        fields: dict
            matching fields in the API structure and our data-view
        db: DataStorage
            pointer to an instance of the class responsible for storing data
        extractor: Extractor
            pointer to an instance of the class responsible for extracting data from text
        headers: dict
            default http header data
        """

        self.api_root = None
        self.fields = None
        self.db = DataStorage()
        self.extractor = Extractor(db=self.db)
        self.headers = {
            'User-Agent': generate_user_agent()
        }

    @abstractmethod
    def fetch_vacancies_portion(self, page_num):
        """Get one job page from API by number."""

        pass

    @staticmethod
    def get_field_from_nested_dict(data_dict, map_tuple):
        """Gets a field from a nested dictionary."""

        return reduce(operator.getitem, map_tuple, data_dict)

    def get_ids(self, params, ids_root, str_get_params=''):
        """Returns a tuple of unique vacancy identifiers.
        Parameters:
            params: dict
                GET request parameter dictionary
            ids_root: str
                name of the parent element within which to find
            str_get_params: str
                GET string parameters (optional)
        """

        ids = ()
        response = requests.get(url=self.api_root + str_get_params, params=params, headers=self.headers)
        if response.status_code == 200:
            ids = tuple(x['id'] for x in response.json()[ids_root])
        return ids

    def get_vacs_by_ids(self, ids=None):
        """Returns tuple of vacancies with specified identifiers.
        Parameters:
            ids: tuple
                кортеж идентификаторов вакансий, которые нужно получить
        """
        vacs = []
        if ids:
            for vac_id in ids:
                response = requests.get(f'{self.api_root}/{vac_id}', headers=self.headers)
                if response.status_code == 200:
                    vacancy = response.json()
                    vacs.append(vacancy)
        return tuple(vacs)

    def get_vacs_by_root(self, params, data_map=None):
        """Returns tuple of vacancies.
        Parameters:
            params: dict
                dictionary with request parameters
            data_map: tuple
                path to vacancies list inside JSON
        """
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
        """Processes tuple with vacancies objects.
        Parameters:
            vacs: tuple
                vacancies returned by API
        """
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
                            vacancy_url = vacancy[url_map]

                        document = {
                            '_id': _id,
                            'name': vacancy[fields['name']],
                            'description': desc,
                            'pub_date': vacancy[fields['pub_date']],
                            'url': vacancy_url,
                            'key_skills': extracted_skills,
                        }

                        self.db.add_doc(DEF_COL, document)


class BaseHTMLParser(ABC):
    """Base class for HTML-parsers.

    Attributes:
        id: parser instance identifier
    """

    id = None

    def __init__(self):
        """
        Attributes:
            url: URL
                link to categories
            db: DataStorage
                pointer to an instance of the class responsible for storing data
            extractor: Extractor
                pointer to an instance of the class responsible for extracting data from text
            headers: dict
                default http header data
        """
        self.url = None
        self.db = DataStorage()
        self.extractor = Extractor(db=self.db)
        self.headers = {
            'User-Agent': generate_user_agent()
        }

    def parse_url(self, url, params=None):
        """Returns soup-object for concrete url"""
        r = requests.get(url, params=params, headers=self.headers)
        soup = BeautifulSoup(r.text, 'html.parser')

        return soup

    @abstractmethod
    def parse_categories(self):
        """Parses category links"""
        pass

    @abstractmethod
    def parse_vacs_of_current_category(self, params):
        """Parses links to vacancy pages"""
        pass

    @abstractmethod
    def parse_text_of_current_vac(self):
        """Parses skills from text"""
        pass

    @abstractmethod
    def fetch_vacancies_portion(self, page_num):
        """Get one job page by number."""
        pass


class HhParser(BaseParser):
    """ Hh.ru API-parser implementation.

    Inherits the base class BaseParser"""

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
            'url': 'alternate_url',
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
    """GitHub Jobs API-parser implementation.

    Inherits the base class BaseParser"""

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
    """Authentic Jobs API-parser implementation.

    Inherits the base class BaseParser"""

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
    """TheMuse API-parser implementation.

    Inherits the base class BaseParser"""

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


class MonsterParser(BaseHTMLParser):
    """monster.com html-parser implementation.

       Inherits the base class BaseHTMLParser"""

    id = 'mr'

    def __init__(self):
        """
        Attributes:
            self.categories: list
                list of links to category pages
            self.vacs: list
                list of links to vacancy pages
        """
        super().__init__()
        self.url = 'https://www.monster.com/jobs/browse/q-computer-jobs'

        self.categories = []
        self.vacs = []

        self.pattern_for_categories = r'https:\/\/www\.monster\.com\/jobs\/q.+'
        self.pattern_for_vacs = r'https:\/\/job-openings\.monster\.com\/'
        self.pattern_for_skills = r'(?![a-z])(?![A-Z])[\.?\-?\s?\/?\,?\(?\)?]'

    def parse_categories(self):
        soup = self.parse_url(self.url)
        block_with_links = soup.findAll('ul', class_='card-columns')
        block_with_links = block_with_links[0]
        links = block_with_links.findAll('a')

        for link in links:
            link = link.get('href')
            if re.search(self.pattern_for_categories, link):
                self.categories.append(link)

    def parse_vacs_of_current_category(self, params):
        for category in self.categories:
            soup = self.parse_url(category, params)
            vac = soup.findAll(text=re.compile(self.pattern_for_vacs))
            vac = vac[0]

            for v in re.findall(self.pattern_for_vacs + r'.+', vac):
                self.vacs.append(v[:-3])

    def parse_text_of_current_vac(self):
        pattern_for_title = r'\"title\":(\"[^\"]+\")'
        pattern_for_pub_date = r'\"datePosted\":(\"[^\"]+\")'
        pattern_for_desc = r'\"description\":(\"[^\"]+\")'
        pattern_for_cleaning_desc = r'(<br>|<(\/?)div>|<(\/?)h4>|<!--(START|END)_SECTION_[0-9]-->|<(\/?p>)|<(\/?)b>)'

        for v in self.vacs:
            soup = self.parse_url(v)
            text = soup.findAll('script', type='application/ld+json')
            text = str(text)

            _id = soup.findAll('div', id='trackingIdentification')
            for i in _id:
                _id = i.get('data-job-id')

            if not bool(self.db.get_docs(DEF_COL, {'_id': _id}, 1)):
                key_skills = self.extractor.strip_html_tags(text)
                key_skills = self.extractor.extract_skills(key_skills)

                name = re.search(pattern_for_title, text)
                name = name.group(1)[1:-1]
                description = re.search(pattern_for_desc, text)
                description = description.group(1)[1:-1]
                description = re.sub(pattern_for_cleaning_desc, '', description)
                pub_date = re.search(pattern_for_pub_date, text)
                pub_date = pub_date.group(1)[1:-1]

                document = {
                    '_id': _id,
                    'name': name,
                    'description': description,
                    'pub_date': pub_date,
                    'url': v,
                    'key_skills': key_skills,
                }

                self.db.add_doc(DEF_COL, document)

    def fetch_vacancies_portion(self, page_num):
        params = {
            'stpage': '1',
            'page': str(page_num)
        }
        self.parse_categories()
        self.parse_vacs_of_current_category(params)
        self.parse_text_of_current_vac()


class ParserFabric:
    """Parser factory. Generates an instance of the parser of the required type.

    Attributes:
        parsers: dict
            matching parser identifiers and their classes for convenient generation
    """

    def __init__(self):
        self.parsers = {
            HhParser.id: HhParser,
            GitHubParser.id: GitHubParser,
            AuthenticJobsParser.id: AuthenticJobsParser,
            TheMuseParser.id: TheMuseParser,
            MonsterParser.id: MonsterParser
        }

    @property
    def parsers_ids(self):
        """Returns a tuple of all available parsers to generate"""
        return tuple(self.parsers.keys())

    def spawn(self, name):
        """Generates a parser instance by its identifier"""
        return self.parsers[name]()


# # ----- FOR TEST USE ONLY! -----
# if __name__ == '__main__':
    # f = ParserFabric()
    # print(f.spawn('hh').fetch_vacancies_portion(1))
    # print(f.spawn('aj').fetch_vacancies_portion(1))
    # print(f.spawn('gh').fetch_vacancies_portion(2))
    # print(f.spawn('ms').fetch_vacancies_portion(4))
    # print(f.spawn('mr').fetch_vacancies_portion(2))
# # ----- FOR TEST USE ONLY! -----
