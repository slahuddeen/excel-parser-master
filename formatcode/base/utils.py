# coding: utf-8

from __future__ import division, print_function, unicode_literals

from abc import ABCMeta


class Singleton(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class cached_property(object):
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls=None):
        result = instance.__dict__[self.func.__name__] = self.func(instance)
        return result


def is_digit(value):
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
