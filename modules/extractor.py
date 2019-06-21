#!/usr/bin/python
# -*- coding: utf-8 -*-
import re


class Extractor:
    TAG_RE = re.compile(r'<[^>]+>')
    synonyms = (
        ['developer', 'программист', 'разработчик'],
    )

    def __init__(self, db):
        self.ref = db.get_key_skills_ref()

    def check_synonyms(self, word):
        seq = [x for x in self.__class__.synonyms if word in x]
        if seq:
            return list(filter(lambda x: x != word, seq[0]))

    def strip_html_tags(self, text):
        return self.__class__.TAG_RE.sub('', text)

    @staticmethod
    def has_cyrillic(text):
        return bool(re.search('[а-яА-Я]', text))

    def purge_cyrrilic_skills(self, skill_list):
        return [x for x in skill_list if not self.has_cyrillic(x)]

    def extract_skills(self, text):
        key_skills = set()
        if self.ref:
            for skill in self.ref:
                if len(skill) > 1:
                    if re.search(r"\b" + re.escape(skill) + r"\b", text, re.MULTILINE | re.IGNORECASE):
                        if not self.has_cyrillic(skill):
                            key_skills.add(skill)
        return list(key_skills)
