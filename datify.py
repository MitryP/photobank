# encoding: utf-8
# module datify

"""This module allows to extract valid date from user input.
Datify can identify separate parts of dates, e.g. '2021', 'july', '6th'.
Also, module functions can be used to identify separate parts of date through class' static methods:
is_day(day), is_year(year), is_digit_month(month) for digit representation of month, and is_alpha_month(month) for alphabethic
representation of month.
User input is processed through class 'Datify'. Code  `Datify(string).date()`  will return datetime object if all
parameters were given in the string. Otherwise it will raise TypeError. To get tuple of all available fields from
string use  `Datify(string).tuple()` To get datetime object or tuple if datetime is unable to be created use
`Datify(string).date_or_tuple()`
Languages supported: English, Russian, Ukrainian.
===
Datify can handle all of the cases of user input listed below and may work with some other cases. Try by yourself before
using:
'06.06.2021'                # Also, '-', '/', and ' ' can be used as separators instead '.', and new separators can be
'6/6/2021'                  # added to  `config['Separators']`
'July, 6th, 2021'
'6th of July, 2021'
'Декабрь, 6, 2021'
'6 декабря 2021 года'
'20 січня 2020'
and other.
===
Getting result:
Datify(str).date() -> datetime object or TypeError
Datify(str).tuple() -> tuple (day, month, year)
Datify(str).date_or_tuple() -> datetime object or tuple
===
Extended version of documentation can be found at GitHub: https://github.com/MitryP/datify/
"""
import re

from datetime import datetime
from typing import Optional, Union, Dict

config: Dict[str, Union[set, str]] = {
    'SPLITTERS': {' ', '/', '.', '-'},

    'FORMAT_DAY_DIGIT': r'[0123]?\d$',
    'FORMAT_DAY_ALNUM': r'[0123]?\d\D+$',
    'FORMAT_MONTH_DIGIT': r'[01]?\d$',
    'FORMAT_YEAR_DIGIT': r'([012]\d\d\d$)|(\d\d$)',
    'FORMAT_DATE': r'[12][01]\d\d[01]\d[0123]\d$'
}

Months: Dict[tuple, int] = {
    ('january', 'jan', 'январь', 'січень'): 1,
    ('february', 'feb', 'февраль', 'лютий'): 2,
    ('march', 'mar', 'март', 'березень'): 3,
    ('april', 'apr', 'апрель', 'квітень'): 4,
    ('may', 'май', 'травень'): 5,
    ('june', 'jun', 'июнь', 'червень'): 6,
    ('july', 'jul', 'июль', 'липень'): 7,
    ('august', 'aug', 'август', 'серпень'): 8,
    ('september', 'sep', 'сентябрь', 'вересень'): 9,
    ('october', 'oct', 'октябрь', 'жовтень'): 10,
    ('november', 'nov', 'ноябрь', 'листопад'): 11,
    ('december', 'dec', 'декабрь', 'грудень'): 12
}


def _isSameWord(str1: str, str2: str) -> bool:
    """
    Tries to figure if given strings are the same words in different forms.
    Returns True or False.
    :param str1: str
    :param str2: str
    :return: Bool
    """

    return (len(set(str1).difference(set(str2))) < len(str1) / 2) and (
            len(set(str2).difference(set(str1))) < len(str2) / 2) and (
            str1[0:2] == str2[0:2] if len(str1) < 4 else str1[0:3] == str2[0:3])


def _getWordsList(string: str) -> Optional[list]:
    """
    Returns list of string's elements if given string contains one of the separators. Otherwise returns None.
    :param string: Takes str
    :return: list or None
    """

    for splitter in Datify.splitters:
        if string.find(splitter) > 0:
            return string.split(splitter)

    else:
        return None


class Datify:
    config: dict = config

    splitters: set = config['SPLITTERS']
    day_format_digit: str = config['FORMAT_DAY_DIGIT']
    day_format_alnum: str = config['FORMAT_DAY_ALNUM']
    month_format_digit: str = config['FORMAT_MONTH_DIGIT']
    year_format: str = config['FORMAT_YEAR_DIGIT']
    date_format: str = config['FORMAT_DATE']

    def __init__(self, user_input: Optional[str] = None, year: Optional[int] = None,
                 month: Optional[int] = None, day: Optional[int] = None) -> None:
        """
        Datify class. Tries to extract day, month, and year from given string. Also, can take separate parameters.
        If no parameters are given, raises ValueError.
        :param user_input: Takes str, optional
        :param year: Takes int, optional
        :param month: Takes int, optional
        :param day: Takes int, optional
        """

        self.day, self.month, self.year, self.lost = day, month, year, list()
        if user_input:
            words = _getWordsList(user_input)
            if words:
                for word in words:
                    if self.is_day(word) and not self.day:
                        self.set_day(word)

                    elif (self.is_digit_month(word) or self.is_alpha_month(word)) and not self.month:
                        self.set_month(word)

                    elif self.is_year(word) and not self.year:
                        self.set_year(word)

                    else:
                        self.lost.append(word)

            elif user_input.isdigit() and len(user_input) > 4:
                search = re.search(self.date_format, user_input)
                if search:
                    search_str = search.group(0)
                    self.set_year(search_str[0:4])
                    self.set_month(search_str[4:6])
                    self.set_day(search_str[6:8])

                else:
                    raise ValueError('date was not found')

            elif self.is_day(user_input):
                self.set_day(user_input)

            elif self.is_alpha_month(user_input):
                self.set_month(user_input)

            elif self.is_year(user_input):
                self.set_year(user_input)

            else:
                raise ValueError('unsupported format')

        elif any((year, month, day)):
            self.year = year
            self.month = month
            self.day = day

        else:
            raise ValueError('no date parts were found')

    @staticmethod
    def is_date_part(string: str) -> bool:
        """
        Returns True if given string contains parts of date in formats supported by Datify.
        Returns True or False.
        :param string: Takes str
        :return: bool
        """

        words = _getWordsList(string)
        if words:
            for word in words:
                if any([
                    Datify.is_day(word),
                    Datify.is_digit_month(word),
                    Datify.is_alpha_month(word),
                    Datify.is_year(word)
                ]):
                    return True

            else:
                return False

        else:
            return any([
                    Datify.is_day(string),
                    Datify.is_digit_month(string),
                    Datify.is_alpha_month(string),
                    Datify.is_year(string),
                    Datify.is_date(string)
                ])

    @staticmethod
    def is_date(date: Union[str, int]) -> bool:
        """
        Returns True if given parameter suits format of date ('YYYYMMDD' by default).
        Returns True or False
        :param date: Takes str
        :return: bool
        """

        date = str(date)

        if re.match(Datify.date_format, date):
            return True

        else:
            return False

    @staticmethod
    def find_date(string: str) -> Optional[str]:
        """
        Returns date in general date format from given string if present. Otherwise, returns None
        :param string: Takes str
        :return: str or None
        """

        res = re.search(Datify.date_format[:-1], string)

        if res:
            return res.group(0)

        else:
            return None

    @staticmethod
    def is_day(day: Union[str, int]) -> bool:
        """
        Returns True if given parameter is suits the day format: e.g. '09' or '9,' or '9th'.
        Returns True or False
        :param day: Takes str
        :return: bool
        """

        day = str(day)

        if day.isdigit():
            if re.match(Datify.day_format_digit, day) and 0 < int(day) <= 31:
                return True

            else:
                return False

        else:
            if re.match(Datify.day_format_alnum, day):
                return True

            else:
                return False

    def set_day(self, day: Union[str, int]) -> None:
        """
        Sets day of Datify's object.
        :param day: Takes str or int
        :return: no return
        """

        day = str(day)

        if Datify.is_day(day):
            if day.isdigit():
                self.day = int(day)

            elif re.match(Datify.day_format_alnum, day):
                day_re = re.search(Datify.day_format_digit[0:-1], day)

                if day_re:
                    day_str = day_re.group(0)
                    self.day = int(day_str)

                else:
                    raise ValueError

        else:
            raise ValueError

    @staticmethod
    def is_digit_month(month: Union[str, int]) -> bool:
        """
        Returns True if the given parameter suits digit month format: e.g. '09' or '9'.
        Returns True or False.
        :param month: Takes str
        :return: Bool
        """

        month = str(month)

        if re.match(Datify.month_format_digit, month) and 0 < int(month) <= 12:
            return True

        else:
            return False

    @staticmethod
    def is_alpha_month(string: str) -> bool:
        """
        Returns True if given parameter suits alpha month format: e.g. 'January' or 'jan' or 'январь' or 'января'.
        Returns True or False.
        :param string: Takes str
        :return: Bool
        """

        word = string.lower()
        for month in Months.keys():
            if word in month:
                return True

        for month in Months.keys():
            if any(_isSameWord(word, month_name) for month_name in month):
                return True

        else:
            return False

    @staticmethod
    def get_alpha_month(string: str) -> Optional[int]:
        """
        Returns number of given month name. If not found, returns None.
        :param string: Takes str
        :return: int or None
        """

        word = string.lower()
        for month in Months.keys():
            if word in month:
                return Months[month]

        for month in Months.keys():
            if any(_isSameWord(word, month_name) for month_name in month):
                return Months[month]

        else:
            return None

    def set_month(self, month: Union[str, int]) -> None:
        """
        Sets month of Datify's object. Takes number of a month or its name.
        If given string isn't a month name, raises ValueError.
        :param month: Takes str or int
        :return: no return
        """

        month = str(month)

        if Datify.is_digit_month(month):
            self.month = int(month)

        elif Datify.is_alpha_month(month):
            self.month = Datify.get_alpha_month(month)

        else:
            raise ValueError

    @staticmethod
    def is_year(year: Union[str, int]) -> bool:
        """
        Returns True if given parameter is suitable for the year format: e.g. '14' or '2014'.
        Returns True or False.
        :param year: Takes str
        :return: Bool
        """

        year = str(year)

        if re.match(Datify.year_format, year):
            return True

        else:
            return False

    def set_year(self, year: Union[str, int]) -> None:
        """
        Sets year of Datify's object.
        :param year: Takes str or int
        :return: no return
        """

        year = str(year)

        if Datify.is_year(year):
            if len(year) == 4:
                self.year = int(year)

            else:
                self.year = int(f'20{year}')

        else:
            raise ValueError

    def date(self) -> datetime:
        """
        Returns datetime object if all needed parameters are known. Otherwise raises TypeError.
        :return: datetime object
        """

        return datetime(year=self.year, month=self.month, day=self.day)

    def tuple(self) -> tuple:
        """
        Returns tuple of all parameters.
        :return: tuple
        """

        return self.day, self.month, self.year

    def date_or_tuple(self) -> Union[datetime, tuple]:
        """
        Returns datetime object if all needed parameters are known. Otherwise returns tuple of all parameters.
        It's not recommended to use because it can return different types, but in some cases it may be useful.
        :return: datetime object or tuple
        """

        try:
            return datetime(year=self.year, month=self.month, day=self.day)

        except TypeError:
            return self.tuple()

    def __repr__(self):
        return f'<Datify object {self.tuple()}>'
