from datetime import datetime
from dataclasses import dataclass
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


@dataclass
class Event:
    summary: str
    description: str
    location: str
    start: datetime
    end: datetime


class GCalendar:
    def __init__(self, calendar_id: str) -> None:
        self.calendar_id: str = calendar_id
        self.__loadCredentials()
        self.service = build("calendar", "v3", credentials=self.creds)

    def __loadCredentials(self) -> None:
        SCOPES = ["https://www.googleapis.com/auth/calendar.events.owned"]
        self.creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if (
            (not self.creds or not self.creds.valid)
            and self.creds
            and self.creds.expired
            and self.creds.refresh_token
        ):
            self.creds.refresh(Request())

    def createEvent(self, event: Event):
        event_result = (
            self.service.events()
            .insert(
                calendarId=self.calendar_id,
                body={
                    "summary": event.summary,
                    "description": event.description,
                    "start": {"dateTime": event.start},
                    "end": {"dateTime": event.end},
                    "location": event.location,
                },
            )
            .execute()
        )

        # print("created event")
        # print("id: ", event_result['id'])
        # print("summary: ", event_result['summary'])
        # print("starts at: ", event_result['start']['dateTime'])
        # print("ends at: ", event_result['end']['dateTime'])

    def listEvents(self):
        now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=now,
                maxResults=1000,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event)

    def getEvents(self, start, end):
        events_result = (
            self.service.events()
            .list(
                calendarId=self.calendar_id,
                timeMin=start,
                timeMax=end,
                maxResults=1000,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    def deleteEvent(self, event_id):
        self.service.events().delete(
            calendarId=self.calendar_id,
            eventId=event_id,
        ).execute()
