import pytest
from datetime import datetime

from formatcode.convert.fc import FormatCode
from formatcode.convert import handlers

def work():
    print("hello")

# currently not working
def test_format_group_001():
    fc = FormatCode(r'" "#,##0.00" "[$€-401]" ";"-"#,##0.00" "[$€-401]" ";" -"00" "[$€-401]" "')
    assert fc.format(123) == r' 123.00 € '
    assert fc.format(25.83) == r' 25.83 € '
    assert fc.format(148.83) == r' 148.83 € '
    assert fc.format(82) == r' 82.00 € '
    assert fc.format(17.22) == r' 17.22 € '
    assert fc.format(99.22) == r' 99.22 € '
    assert fc.format(95) == r' 95.00 € '
    assert fc.format(19.95) == r' 19.95 € '
    assert fc.format(114.95) == r' 114.95 € '
    assert fc.format(137.95) == r' 137.95 € '

def test_format_group_002():
    fc = FormatCode(r'" "#,##0.00" "[$€-401]" ";"-"#,##0.00" "[$€-401]" ";" -"00" "[$€-401]" ";" "@" "')
    assert fc.format(148.83) == r' 148.83 € '
    assert fc.format(99.22) == r' 99.22 € '
    assert fc.format(114.95) == r' 114.95 € '
    assert fc.format(137.95) == r' 137.95 € '

def test_format_group_003():
    fc = FormatCode(r'" "[$£-809]#,##0.00" ";"-"[$£-809]#,##0.00" ";')
    assert fc.format(72) == r' £72.00 '
    assert fc.format(80) == r' £80.00 '

def test_format_group_004():
    fc = FormatCode(r'" "[$£-809]#,##0.00" ";"-"[$£-809]#,##0.00" ";" "[$£-809]"-"00" ";" "@" "')
    assert fc.format(18) == r' £18.00 '
    assert fc.format(20) == r' £20.00 '
    assert fc.format(152) == r' £152.00 '
    assert fc.format(0) == r' £-00 '

def test_format_group_005():
    fc = FormatCode(r'" "[$£-809]* #,##0.00" ";"-"[$£-809]* #,##0.00" ";" "')
    assert fc.format(180) == r' £180.00 '
    assert fc.format(0) == r' '
    assert fc.format(220) == r' £220.00 '
    assert fc.format(27.5) == r' £27.50 '
    assert fc.format(25) == r' £25.00 '
    assert fc.format(540) == r' £540.00 '
    assert fc.format(88) == r' £88.00 '
    assert fc.format(330) == r' £330.00 '
    assert fc.format(333.5) == r' £333.50 '
    assert fc.format(69) == r' £69.00 '

def test_format_group_006():
    fc = FormatCode(r'"$"#,##0.00_);[Red]\("$"#,##0.00\)')
    assert fc.format(350) == r'$350.00 '
    assert fc.format(9715) == r'$9,715.00 '
    assert fc.format(9380) == r'$9,380.00 '
    assert fc.format(41540) == r'$41,540.00 '
    assert fc.format(7245) == r'$7,245.00 '
    assert fc.format(9417) == r'$9,417.00 '
    assert fc.format(490) == r'$490.00 '
    assert fc.format(26460) == r'$26,460.00 '
    assert fc.format(31155) == r'$31,155.00 '

def test_format_group_007():
    fc = FormatCode(r'"$"#,##0.00_);[Red]\("$"#,##0.00\);')
    assert fc.format(350) == r'$350.00 '
    assert fc.format(0) == r''
    assert fc.format(9715) == r'$9,715.00 '
    assert fc.format(41540) == r'$41,540.00 '
    assert fc.format(9045) == r'$9,045.00 '
    assert fc.format(9417) == r'$9,417.00 '
    assert fc.format(15600) == r'$15,600.00 '
    assert fc.format(9315) == r'$9,315.00 '
    assert fc.format(16800) == r'$16,800.00 '
    assert fc.format(2465) == r'$2,465.00 '

def test_format_group_08():
    fc = FormatCode(r'"£"#,##0.00')
    assert fc.format(18) == r'£18.00'
    assert fc.format(90) == r'£90.00'
    assert fc.format(26.5) == r'£26.50'
    assert fc.format(312) == r'£312.00'
    assert fc.format(0) == r'£0.00'
    assert fc.format(46.25) == r'£46.25'
    assert fc.format(455) == r'£455.00'
    assert fc.format(46.2) == r'£46.20'
    assert fc.format(2751.59) == r'£2,751.59'
    assert fc.format(-315) == r'-£315.00'

def test_format_group_09():
    fc = FormatCode(r'"£"#,##0.00;[Red]"£"#,##0.00')
    assert fc.format(33) == r'£33.00'
    assert fc.format(22) == r'£22.00'
    assert fc.format(506) == r'£506.00'

def test_format_group_010():
    fc = FormatCode(r'"£"#,##0.00;[Red]\-"£"#,##0.00')
    assert fc.format(35) == r'£35.00'
    assert fc.format(210) == r'£210.00'
    assert fc.format(185) == r'£185.00'
    assert fc.format(323) == r'£323.00'
    assert fc.format(455) == r'£455.00'
    assert fc.format(1553.09) == r'£1,553.09'
    assert fc.format(200) == r'£200.00'
    assert fc.format(1983.09) == r'£1,983.09'
    assert fc.format(1178.48) == r'£1,178.48'
    assert fc.format(3609.5) == r'£3,609.50'

def test_format_group_011():
    fc = FormatCode(r'"£"#,##0.00_);[Red]\("£"#,##0.00\)')
    assert fc.format(128.75) == r'£128.75 '
    assert fc.format(120) == r'£120.00 '
    assert fc.format(103.75) == r'£103.75 '
    assert fc.format(779.07) == r'£779.07 '

def test_format_group_012():
    fc = FormatCode(r'"£"#,##0;[Red]\-"£"#,##0')
    assert fc.format(22) == r'£22'
    assert fc.format(110) == r'£110'
    assert fc.format(138) == r'£138'