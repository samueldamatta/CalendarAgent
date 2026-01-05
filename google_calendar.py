import os.path
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleCalendarClient:
    def __init__(self):
        self.creds = None
        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticates the user and returns the service object."""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("The file 'credentials.json' was not found. Please provide it from Google Cloud Console.")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
        except HttpError as error:
            print(f'An error occurred: {error}')

    def list_events(self, time_min: str, time_max: str):
        """Lists events between time_min and time_max."""
        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            return events_result.get('items', [])
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def create_event(self, summary: str, start_time: str, end_time: str, description: str = ""):
        """Creates an event on the calendar."""
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Sao_Paulo',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Sao_Paulo',
            },
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return event
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def check_availability(self, date_str: str):
        """
        Checks availability for a specific date.
        date_str should be in 'YYYY-MM-DD' format.
        """
        # Horário comercial das 08:00 às 18:00 (ajustando para o fuso do Brasil -03:00)
        time_min = f"{date_str}T08:00:00-03:00"
        time_max = f"{date_str}T18:00:00-03:00"
        
        events = self.list_events(time_min, time_max)
        
        if not events:
            return f"O dia {date_str} está totalmente disponível das 08:00 às 18:00."
        
        busy_slots = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Formata os horários para ficarem mais legíveis (ex: 09:00 às 10:00)
            if 'T' in start:
                start_time = start.split('T')[1][:5]
                end_time = end.split('T')[1][:5]
                busy_slots.append(f"{start_time} às {end_time}")
            else:
                busy_slots.append(f"Dia todo: {event['summary']}")
        
        return f"No dia {date_str}, os seguintes horários já estão ocupados: " + ", ".join(busy_slots)
