# coding: utf-8

from __future__ import division, print_function, unicode_literals

from formatcode.convert.mask import Mask


def test_mask():
    mask = Mask()
    assert mask.tokens == []
    assert len(mask) == 0

    mask.add('#', mask.PH)
    assert len(mask) == 1

    mask.add('one', mask.STRING)
    assert len(mask) == 2
    mask.add(' ', mask.STRING)
    mask.add('two', mask.STRING)
    assert len(mask) == 2
    assert mask[1].value == 'one two'
    assert mask[1].type == mask.STRING

    mask.add(',', mask.COMMA)
    assert len(mask) == 3
    assert mask[0].value == '#'
    assert mask[0].type == mask.PH
