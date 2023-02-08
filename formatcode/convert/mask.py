# coding: utf-8

from __future__ import division, print_function, unicode_literals


class MaskToken(object):
    def __init__(self, value, value_type):
        self.value = value
        self.type = value_type


class Mask(object):
    STRING = 1
    PH = 2
    COMMA = 3
    AM_PM = 4
    SLASH = 5
    E = 6

    def __init__(self):
        self.tokens = []

    def __getitem__(self, idx):
        return self.tokens[idx]

    def add(self, value, value_type):
        if self.tokens and value_type == self.STRING and self[-1].type == value_type:
            self[-1].value += value
        else:
            self.tokens.append(MaskToken(value, value_type))

    def __len__(self):
        return len(self.tokens)
