from __future__ import print_function
import meetup.api
import datetime
import httplib2
import os
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'google_calendar_secret.json'
APPLICATION_NAME = 'Meetup Calendar Integration'
meetupToken = os.environ.get('MEETUP_ACCESS_TOKEN', None)
meetupMember = os.environ.get('MEETUP_MEMBER_ID', None)
googleCalendar = os.environ.get('GOOGLE_CALENDAR_ID', None)
all_events = {'member_id': meetupMember}
meetup_client = meetup.api.Client(meetupToken)
my_events = meetup_client.GetEvents(all_events)
events_dict = my_events.results


def get_meetups():
    """Gets all events from Meetups user is subscribed to.

    If no end time is available, the event defaults to 2 hours.

    Individual event data is put in a dictionary json format acceptable by the Google
        Calendar API and appended to a list.

    """
    event_list = []
    calendar_dict = {}
    for item in events_dict:
        url = item.get('event_url')
        name = item.get('name')
        group = item.get('group').get('name')
        summary = "{} - {}".format(name, group)
        description = item.get('description')
        address = item.get('address_1')
        start_sec = item.get('time') / 1000.0
        try:
            end_sec = (item.get('duration') / 1000.0) + start_sec
        except TypeError:
            end_sec = start_sec + 7200.0
        start_time = datetime.datetime.fromtimestamp(start_sec).strftime(('%Y-%m-%dT%H:%M:%S-07:00'))
        end_time = datetime.datetime.fromtimestamp(end_sec).strftime(('%Y-%m-%dT%H:%M:%S-07:00'))

        calendar_dict = {
            'summary': summary,
            'location': address,
            'description': description,
            'source': {
            'title': group,
            'url': url
            },
            'start': {
              'dateTime': start_time,
              'timeZone': 'America/Los_Angeles',
            },
            'end': {
              'dateTime': end_time,
              'timeZone': 'America/Los_Angeles',
            },
            'recurrence': [
              'RRULE:FREQ=DAILY;COUNT=1'
             ],
            'reminders': {
              'useDefault': False,
              'overrides': [
                {'method': 'popup', 'minutes': 30},
              ],
            }
        }

        event_list.append(calendar_dict)
    return event_list

def get_gcal_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gcal-event-insert.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def add_to_calendar():
    """Adds Meetup Events to Google Calendar """
    credentials = get_gcal_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    event_list = get_meetups()
    for event in event_list:
        service.events().insert(calendarId=googleCalendar, body=event).execute()
        print("events added for {}".format(event.get('summary')))

add_to_calendar()
