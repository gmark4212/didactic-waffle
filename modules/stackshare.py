#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


class SkillCrawler:
    url = 'https://stackshare.io/tools/'

    @staticmethod
    def get_soup(url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
            'Referer': url
        }
        try:
            page = requests.get(url, headers=headers)
            soup = BeautifulSoup(page.text, 'html.parser')
        except:
            print('NO SOUP! ', url)
            soup = None
        return soup

    def parse(self, chapter):
        print('===============> ', chapter)
        page = 0
        skills = []

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

                    skill = {
                        'name': i.find('span', {'id': 'service-name-trending'}).text,
                        'desc': i.find('div', {'class': 'trending-description'}).text.strip(),
                        'ctg': ctg,
                        'site': i.find('a', href=True, text='Visit Website')['href'],
                        'logo': i.find('div', {'class': 'tool-logo'}).find('img')['src']
                    }
                    if skill:
                        skills.append(skill)
                        print(skill)
            else:
                break


if __name__ == '__main__':
    sc = SkillCrawler()
    sc.parse('trending')
    sc.parse('top')
    sc.parse('new')
