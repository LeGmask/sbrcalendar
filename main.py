import datetime
import os
import json
import pytz
from requests.api import delete

from src.gcalendar import *
from src.grr import *

with open(os.path.join(os.path.dirname(__file__), './config.json'), encoding='utf-8') as file:
	configs = json.load(file)

# TODO: Refactor checkForDuplicate
# Avoid: Use of a global
def checkForDuplicate(course):
	global actual_events
	for i, event in enumerate(actual_events):
		if course.sha1() == event["description"]:
			print(f"skipping {course.name}")
			del actual_events[i]
			return True
	return False

today = datetime.datetime.today()


for config in configs:
	global actual_events
	grr = Grr(config["keyword"])
	calendar = GCalendar(config["calendar"])
	for i in range(30):
		day = today + datetime.timedelta(days = i)
		courses = grr.getCourses(day.year, day.month, day.day)

		start = datetime.datetime(day.year, day.month, day.day).astimezone(pytz.timezone('Europe/Paris'))
		end = start + datetime.timedelta(days=1)
		
		actual_events = calendar.getEvents(start.isoformat(), end.isoformat())
		for course in courses:
			if (actual_events and not checkForDuplicate(course)
				or not actual_events):			
				calendar.createEvent(Event(course.name, course.sha1(), course.place, course.date[0], course.date[1]))
		for event in actual_events:
			calendar.deleteEvent(event["id"])
