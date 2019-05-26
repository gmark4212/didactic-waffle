#!/usr/bin/python
# -*- coding: utf-8 -*-
import re


class SkillsExtractor:
    def __int__(self):
        pass

    def __init__(self):
        self.TAG_RE = re.compile(r'<[^>]+>')

    def strip_html_tags(self, text):
        return self.TAG_RE.sub('', text)

    def extract_skills(self, text):
        pass
