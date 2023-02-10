from formatcode.convert.fc import FormatCode
from formatcode.convert import handlers

def test():
    fc = FormatCode(r'" "#,##0.00" "[$€-401]" ";"-"#,##0.00" "[$€-401]" ";" -"00" "[$€-401]" "')
    assert fc.format(123) == r' 123.00 € '
    fc_1 = FormatCode('0,,;\\-0" "?/10%;General;"Hello, "@\\!')
    assert fc_1.format(123) == r'123'

print(test())