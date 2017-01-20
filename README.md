# Meetup + Google Calendar Integration
Adds all events of [Meetups](https://www.meetup.com/) user is part of to their Google Calendar.

Allows users to manage their Meetup calendar with the same tool they manage their work or personal calendars with. No need to RSVP to event to have it added to Google Calendar (you should still RSVP if you are attending :-) ).

Notifies calendar user 30 minutes before an event.

Share your calendar with individuals or across your organization.

Utilizes the [Meetup API](https://www.meetup.com/meetup_api/) and [Google Calendar API](https://developers.google.com/google-apps/calendar/)

## How it Works
* Gets all events of Meetup user is part of.
* Checks Google Calendar to see if event is already in calendar.
* Updates calendar if there are new events.

## Setup

* git clone this repository
* install [pip](https://pip.pypa.io/en/stable/installing/)
* from the project root `pip install requirements.txt`

### Turn on the Google Calendar API (from [Google Calendar API Quickstart Guide](https://developers.google.com/google-apps/calendar/quickstart/python))

* Use this [wizard](https://console.developers.google.com/start/api?id=calendar) to create or select a project in the Google Developers Console and automatically turn on the API. Click Continue, then Go to credentials.
* On the Add credentials to your project page, click the Cancel button.
* At the top of the page, select the OAuth consent screen tab. Select an Email address, enter a Product name if not already set, and click the Save button.
* Select the Credentials tab, click the Create credentials button and select OAuth client ID.
* Select the application type Other, enter the name "Meetup Calendar Integration", and click the Create button.
* Click OK to dismiss the resulting dialog.
* Click the file_download (Download JSON) button to the right of the client ID.
* Move this file to your working directory and rename it `google_calendar_secret.json`.

### Get Google Calendar ID
* Visit https://calendar.google.com/ and create a Google Calendar, or use an existing calendar you have view and modify access to.
* Select the calendar and visit `Calendar Settings`
* Copy your calendar id and set it as the environment variable `GOOGLE_CALENDAR_ID`


### Get Meetup API Tokens

* Login to Meetup and visit https://www.meetup.com/meetup_api/
* Select `API Key` and save your API Key. Set as the environment variable `MEETUP_ACCESS_TOKEN`
* Visit https://www.meetup.com/account/ and copy your User ID (just the numbers). Set it as `MEETUP_MEMBER_ID`.


### Update Google Calendar

* from the project root, run `python update_calendar.py`
* All events from all Meetups you are subscribed to are now on your Google Calendar.

#### Known Issues
See issues tab for details.
