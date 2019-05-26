#!/usr/bin/python
# -*- coding: utf-8 -*-

synonyms = (
    ['developer', 'программист', 'разработчик'],
)


def check_synonyms(word):
    seq = [x for x in synonyms if word in x]
    if seq:
        return list(filter(lambda x: x != word, seq[0]))
