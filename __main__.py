from formatcode.convert.fc import FormatCode
from formatcode.convert import handlers

def test():
    fc = FormatCode(r'" "#,##0.00" "[$€-401]" ";"-"#,##0.00" "[$€-401]" ";" -"00" "[$€-401]" "')
    assert fc.format(123) == r' 123.00 € '

print(test())