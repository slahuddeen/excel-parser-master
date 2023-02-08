# coding: utf-8

from __future__ import division, print_function, unicode_literals

from six import add_metaclass

from formatcode.base.utils import cached_property, Singleton, is_digit


def test_singleton():
    @add_metaclass(Singleton)
    class A(object):
        pass

    @add_metaclass(Singleton)
    class B(object):
        pass

    assert id(A()) == id(A())
    assert id(B()) == id(B())
    assert id(A()) != id(B())


def test_cached_property():
    class A(object):
        def __init__(self):
            self._counter = 0

        @cached_property
        def counter(self):
            self._counter += 1
            return self._counter

    a = A()
    assert a._counter == 0
    assert a.counter == 1
    assert a.counter == 1

    a.counter = 3
    assert a._counter == 1
    assert a.counter == 3


def test_is_digit():
    assert is_digit(1234) is True
    assert is_digit(-1234) is True
    assert is_digit(1234.1234) is True
    assert is_digit(-1234.1234) is True

    assert is_digit('1234') is True
    assert is_digit('-1234') is True
    assert is_digit('1234.1234') is True
    assert is_digit('-1234.1234') is True

    assert is_digit(None) is False
    assert is_digit('string') is False
    assert is_digit('-') is False
    assert is_digit(type) is False
    assert is_digit('') is False
