from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime

class GoogleCalendarService:
    def __init__(self, token_info: dict):
        self.creds = Credentials.from_authorized_user_info(token_info)
        self.service = build('calendar', 'v3', credentials=self.creds)

    def create_event(self, summary: str, description: str, start_time: datetime, end_time: datetime, attendee_email: str) -> str:
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'UTC'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'UTC'},
            'attendees': [{'email': attendee_email}],
        }
        try:
            created_event = self.service.events().insert(calendarId='primary', body=event).execute()
            return created_event.get('id')
        except Exception as e:
            print(f"Google Calendar create error: {str(e)}")
            return None
