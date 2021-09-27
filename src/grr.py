from dataclasses import dataclass
import datetime
import re
from typing import List
from bs4 import BeautifulSoup
import hashlib
import pytz

import requests


@dataclass
class Course:
    """
    Each course is stored in a normalized item to generate a hash (detect if the course has changed)
    """
    name: str
    place: str
    date: List[datetime.datetime]

    def sha1(self):
        return hashlib.sha1((self.name + self.place + ''.join(self.date)).encode('utf-8')).hexdigest()


class Grr:
    def __init__(self, keyword) -> None:
        self.keyword = keyword

    def getCourses(self, year, month, day):
        self.courses = []
        self.__get_page(year, month, day)
        self.__parse_page(year, month, day)
        return self.courses

    def __parse_page(self, year, month, day):
        soup = BeautifulSoup(self.page, 'html.parser')
        soup = soup.find("table", {"class": "table-bordered table-striped"})
        rows = soup.find_all("tr")

        places = [place.getText().strip().split("\n")[0] for place in rows[0].find_all(
            "th")]  # we create the array with the room names

        del rows[:2]
        self.courses = []
        rows = [rows[i].find_all("td") for i in range(len(rows))]

        for i in range(len(rows)):
            for j in range(len(rows[i])):
                if rows[i][j].has_attr("rowspan") and int(rows[i][j].get('rowspan')) > 1:
                    delay = int(rows[i][j].get('rowspan'))
                    for k in range(i+1, i+delay-1):
                        rows[k].insert(j, BeautifulSoup(
                            '<td class="empty_cell "></td>', 'html.parser'))

        for row in rows:
            for i in range(len(row)):
                if self.keyword in row[i].getText():
                    course = row[i].getText().strip().split('\n')[0]
                    date = []
                    if re.findall(r'[0-9]{1,2}h([0-9]{2})?-[0-9]{1,2}h([0-9]{2})?', course):
                        result = re.findall(
                            r'([0-9]{1,2}h([0-9]{2})?-[0-9]{1,2}h([0-9]{2})?)', course)

                        raw_date = result[0][0]
                        course = course.replace(result[0][0], '').strip()

                        raw_date = raw_date.split('-')
                        for period in raw_date:
                            date.append([k or '00' for k in period.split('h')])
                    else:
                        raw_date = row[i].getText().strip().split('\n')[1]
                        # Remove "Enseignement licence SU"
                        raw_date = raw_date[:-23]
                        raw_date = raw_date.split(' à ')
                        for period in raw_date:
                            date.append(period.split(':'))
                    datetime_obj = []
                    for period in date:
                        datetime_str = f"{year}-{month}-{day} {period[0]}:{period[1]}"
                        datetime_obj.append(datetime.datetime.strptime(
                            datetime_str, '%Y-%m-%d %H:%M').astimezone(pytz.timezone('Europe/Paris')).isoformat())
                    self.courses.append(
                        Course(course, places[i], datetime_obj))
                    break

    def __get_page(self, year, month, day):
        self.page = requests.get(
            f"http://application.sb-roscoff.fr/intranet/grr/day.php?year={year}&month={month}&day={day}&area=10").text
