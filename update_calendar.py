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
import re

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

def get_meetup_events():
    '''Meetup API Call. Returns raw event data of Meetups user is subscribed to.'''
    all_events = {'member_id': meetupMember}
    meetup_client = meetup.api.Client(meetupToken)
    my_events = meetup_client.GetEvents(all_events)
    raw_events_list = my_events.results
    return raw_events_list

def get_useful_data():
    '''
        Takes raw event data and extracts data needed for Google Calendar POST request.
        Lists event location as N/A if not available on Meetup.
        Event defaults to 2 hours if event end time is not listed.
    '''
    raw_events_list = get_meetup_events()
    clean_events_list = []
    clean = re.compile('<.*?>')
    for raw_event in raw_events_list:
        url = raw_event.get('event_url')
        name = raw_event.get('name')
        group = raw_event.get('group').get('name')
        summary = "{} - {}".format(name, group)
        html_description = raw_event.get('description')
        description = re.sub(clean, '', html_description)
        venue = raw_event.get('venue')
        try:
            location = "{}, {}".format(venue.get('address_1'), venue.get('city'))
        except AttributeError:
            location = "N/A"
        start_sec = raw_event.get('time') / 1000.0
        try:
            end_sec = (raw_event.get('duration') / 1000.0) + start_sec
        except TypeError:
            end_sec = start_sec + 7200.0
        start_time = datetime.datetime.fromtimestamp(start_sec).strftime(('%Y-%m-%dT%H:%M:%S-07:00'))
        end_time = datetime.datetime.fromtimestamp(end_sec).strftime(('%Y-%m-%dT%H:%M:%S-07:00'))
        event_data = [url, name, group, summary, description, location, start_time, end_time]
        clean_events_list.append(event_data)
    return clean_events_list


def format_event_data():
    """
        Formats cleaned event data for Google Calendar POST request.
        Appends events to a list.
    """
    clean_events_list = get_useful_data()
    calendar_list = []
    for clean_event in clean_events_list:
        url, name, group, summary, description, location, start_time, end_time = clean_event
        gcal_event = {
            'summary': summary,
            'location': location,
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

        calendar_list.append(gcal_event)
    return calendar_list


def get_gcal_credentials():
    """Gets valid user Google Calendar credentials from storage.
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

def check_calendar():
    """Gets current calendar event summaries and start times. """
    credentials = get_gcal_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    page_token = None
    existing_events = []
    while True:
        events = service.events().list(calendarId=googleCalendar, pageToken=page_token).execute()
        for event in events['items']:
            existing_events.append({'summary': event.get('summary'), 'start': event.get('start').get('dateTime')})
        page_token = events.get('nextPageToken')
        if not page_token:
                break
    return existing_events

def add_to_calendar():
    """
    Compares event summary and start time to that of existing events.
    Adds event to calendar the summary and start time is not already in calendar.
    """
    credentials = get_gcal_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    calendar_list = format_event_data()
    existing_events = check_calendar()
    for new_event in calendar_list:
        summary = new_event.get('summary')
        start = new_event.get('start').get('start_time')
        if not any(d.get('start', None) == start for d in existing_events):
            if not any(d.get('summary', None) == summary for d in existing_events):
                service.events().insert(calendarId=googleCalendar, body=new_event).execute()
                print("events added for {}".format(new_event.get('summary')))

                
add_to_calendar()
