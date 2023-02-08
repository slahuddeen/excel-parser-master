# coding: utf-8

from __future__ import division, print_function, unicode_literals

import pytest

from formatcode.convert.errors import PartsCountError
from formatcode.convert.fc import FormatCode
from formatcode.convert.parts import NegativePart, PositivePart, StringPart, ZeroPart


def test_parts_from_tokens():
    fc = FormatCode('0.0;\\-0.0;General;"Hello, "@')

    assert isinstance(fc.parts[0], PositivePart)
    assert len(fc.parts[0].tokens) == 3

    assert isinstance(fc.parts[1], NegativePart)
    assert len(fc.parts[1].tokens) == 4

    assert isinstance(fc.parts[2], ZeroPart)
    assert len(fc.parts[2].tokens) == 1
    assert isinstance(fc.else_part, ZeroPart)

    assert isinstance(fc.parts[3], StringPart)
    assert len(fc.parts[3].tokens) == 2

    with pytest.raises(PartsCountError):
        FormatCode('0.0;\\-0.0;General;"Hello, "@;0.0')

    fc = FormatCode('0.0')
    assert fc.parts[1].tokens is None
    assert fc.parts[2].tokens is None
    assert fc.parts[3].tokens is None
