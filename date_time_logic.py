# in - value and format string
# out - excel formated string
import datetime
from sys import platform


if __name__ == "__main__":
    print("start!")

    def format_datetime(date_time: datetime, format: str) -> str:
        """ Finds and replaces the Microsoft datetime with the Python datetime."""
        # lower cases the Microsoft datetime so that we can see where Python has replaced it 
        format_string = format.lower()

        # when printing it takes off the padded first zero, operating system excape chars
        leading_zero_escape_char = '#' if platform == 'win32' else '-'

        # does time first and then date to avoid changing mins to months
        format_string = format_string.replace('hh', '%H')
        format_string = format_string.replace('h', f'%{leading_zero_escape_char}H')
        format_string = format_string.replace('ss', '%S')
        format_string = format_string.replace('s', f'%{leading_zero_escape_char}S')
        format_string = format_string.replace('H:mm', 'H:%M')
        format_string = format_string.replace('H:m', f'H:%{leading_zero_escape_char}M')
        format_string = format_string.replace('mm:%S', '%M:%S')
        format_string = format_string.replace(f'mm:%{leading_zero_escape_char}S', f'%M:%{leading_zero_escape_char}S')
        format_string = format_string.replace('m:%S', f'%{leading_zero_escape_char}M:%S')
        format_string = format_string.replace(f'm:%{leading_zero_escape_char}S', f'%{leading_zero_escape_char}M:%{leading_zero_escape_char}S')
        format_string = format_string.replace('am/pm', '%p')

        format_string = format_string.replace("yyyy", "%Y")
        format_string = format_string.replace("yy", "%y")
        format_string = format_string.replace("mmmm", "%B")
        format_string = format_string.replace("mmm", "%b")
        format_string = format_string.replace("mm",  "%m")
        format_string = format_string.replace("m",  f"%{leading_zero_escape_char}m")
        format_string = format_string.replace("dddd", "%A")
        format_string = format_string.replace("ddd", "%a")
        format_string = format_string.replace("dd", "%d")
        format_string = format_string.replace("d",  f"%{leading_zero_escape_char}d")

        return date_time.strftime(format_string)

    def format_text(text: str, format: str) -> str:
        if format[-1] == '@':
            return format.strip("@") + text
        else:
            return text + format.strip("@")

    date_time = datetime.datetime(2000, 1, 1, 12, 34, 56)
    date_time_format = "m/d/yyyy\\ h:mm:ss;@"

    text = "bye!"
    text_format = "hello world: @"

    excel_formated = format_datetime(date_time, date_time_format)
    excel_formated_text = format_text(text,text_format)
    print(excel_formated, " 1/1/2000 12:34:56")
