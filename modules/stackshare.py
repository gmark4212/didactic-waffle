#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from modules.storage import DataStorage
from modules.settings import *


class SkillCrawler:
    url = 'https://stackshare.io/tools/'

    def __init__(self):
        self.skills = []
        self.db = DataStorage()

    @staticmethod
    def get_soup(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'Referer': url
        }
        try:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
        except Exception as err:
            print('NO SOUP! ', err, url)
            soup = None
        return soup

    def parse(self, chapter):
        print('===============> ', chapter)
        page = 0

        while True:
            page += 1
            print(page)
            soup = self.get_soup(f'{self.__class__.url}{chapter}?page={page}')
            if not soup:
                break

            divs = soup.find_all('div', {'class': 'trending-item-container'})
            if divs:
                for i in divs:
                    ctg = ''
                    ctg_spn = i.find('span', {'itemprop': 'applicationSubCategory'})
                    if ctg_spn:
                        ctg = ctg_spn.text

                    name = i.find('span', {'id': 'service-name-trending'}).text

                    skill = {
                        'name': name,
                        'desc': i.find('div', {'class': 'trending-description'}).text.strip(),
                        'ctg': ctg,
                        'site': i.find('a', href=True, text='Visit Website')['href'],
                        'logo': i.find('div', {'class': 'tool-logo'}).find('img')['src'],
                        'low': name.lower()
                    }
                    if skill:
                        self.skills.append(skill)
                        print(skill)
            else:
                break
        self.save()

    def save(self):
        if self.skills:
            for parsed_skill in self.skills:
                self.db.add_skill_to_ref(parsed_skill)
            self.skills = []

    def fetch_skills(self):
        self.parse('trending')
        self.parse('top')
        self.parse('new')


# if __name__ == '__main__':
#     crawler = SkillCrawler()
#     crawler.fetch_skills()
#     del crawler
