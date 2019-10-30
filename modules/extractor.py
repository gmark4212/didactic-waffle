#!/usr/bin/python
# -*- coding: utf-8 -*-
import re


class Extractor:
    """Class for extracting data from texts.

    Attributes:
        TAG_RE: precompiled html-tags matching pattern
        synonyms: tuple of lists
            sets of synonym words (not using)
        ref: tuple
            collection of all skills for matching
    """

    TAG_RE = re.compile(r'<[^>]+>')
    synonyms = (
        ['developer', 'программист', 'разработчик'],
    )

    def __init__(self, db):
        self.ref = db.get_key_skills_ref()

    def check_synonyms(self, word):
        """Matches synonyms for a specified word (not using).
        Parameters:
            word: str
                the word for which you need to find synonyms
        """

        seq = [x for x in self.__class__.synonyms if word in x]
        if seq:
            return list(filter(lambda x: x != word, seq[0]))

    def strip_html_tags(self, text):
        """Removes html-tags from the specified string.
        Parameters:
            text: str
                text which you need to purge
        """

        return self.__class__.TAG_RE.sub('', text)

    @staticmethod
    def has_cyrillic(text):
        """Checks whether the text contains cyrillic or not.
        Parameters:
            text: str
                text which you need to check

        Returns: bool
        """

        return bool(re.search('[а-яА-Я]', text))

    def purge_cyrrilic_skills(self, skill_list):
        """Removes skills containing cyrillic from the list.
        Parameters:
            skill_list: list
                list of skills to test

        Returns: list
        """

        return [x for x in skill_list if not self.has_cyrillic(x)]

    def extract_skills(self, text):
        """Finds skills found in the text by comparing with the skills reference.
        Parameters:
            text: str
                description of vacancy or any text to extract skills from

        Returns: list
        """

        key_skills = set()
        if self.ref:
            for skill in self.ref:
                if len(skill) > 1:
                    if re.search(r"\b" + re.escape(skill) + r"\b", text, re.MULTILINE | re.IGNORECASE):
                        if not self.has_cyrillic(skill):
                            key_skills.add(skill)
        return list(key_skills)
