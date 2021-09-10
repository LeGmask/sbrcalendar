import requests
from bs4 import BeautifulSoup
import re

from requests.api import delete

month = "09"
day = "13"

url = f"http://application.sb-roscoff.fr/intranet/grr/day.php?year=2021&month={month}&day={day}&area=10"

html_text = requests.get(url).text
soup = BeautifulSoup(html_text, 'html.parser')


table = soup.find("table", {"class":"table-bordered table-striped"})
rows = table.find_all("tr")

places = [place.getText().strip().split("\n")[0] for place in rows[0].find_all("th")]
print(places)

del rows[:2]
courses = []
new_rows = []
for i in range(len(rows)):
    new_rows.append(rows[i].find_all("td"))
rows = new_rows

delay_list = []

for i in range(len(rows)):
    for j in range(len(rows[i])):
        if rows[i][j].has_attr("rowspan") and int(rows[i][j].get('rowspan')) > 1:
            delay = int(rows[i][j].get('rowspan'))
            for k in range(i+1, i+delay-1):
                rows[k].insert(j, BeautifulSoup('<td class="empty_cell "></td>','html.parser'))
            
for i in range(len(rows)):
    for j in range(len(rows[i])):
        if "LBM1" in rows[i][j].getText():
            courses.append((places[j], rows[i][j].getText()))
            break
    
# courses = [(i, course.getText()) for i, course in enumerate(courses) if "LBM1" in course.getText()]

print(courses)


# print(rows)


# text = soup.getText()
# text = text.replace("\n", "")
# text = text.split("  ")

# print(text)