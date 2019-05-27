#!/usr/bin/python
# -*- coding: utf-8 -*-
import re


class TextWork:
    synonyms = (
        ['developer', 'программист', 'разработчик'],
    )

    def check_synonyms(self, word):
        seq = [x for x in self.__class__.synonyms if word in x]
        if seq:
            return list(filter(lambda x: x != word, seq[0]))


class SkillsExtractor:
    TAG_RE = re.compile(r'<[^>]+>')

    def __init__(self):
        pass

    def strip_html_tags(self, text):
        return self.__class__.TAG_RE.sub('', text)

    def extract_skills(self, text):
        pass


class ExtractorFacade(SkillsExtractor, TextWork):
    pass
