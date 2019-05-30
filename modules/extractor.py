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

    def extract_skills(self, text):
        key_skills = set()
        if self.ref:
            for skill in self.ref:
                if len(skill) > 1:
                    if text.find(skill) >= 0:
                        key_skills.add(skill)
        return list(key_skills)
