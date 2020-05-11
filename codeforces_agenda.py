from __future__ import print_function
import datetime
import pickle
import os.path
import urllib.request
import json
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_codeforces_contests():
    contests = []
    flag = False
    with urllib.request.urlopen("https://codeforces.com/api/contest.list?gym=false") as url:
        codeforces_data = json.loads(url.read().decode())
        if codeforces_data['status'] == 'OK':
            flag = True
            for contest in codeforces_data['result']:
                if contest['phase'] == 'BEFORE':
                    if 'Div. 2' in contest['name']:
                        contests.append({'id': contest['id'], 'name': contest['name'], 'startDate': datetime.datetime.fromtimestamp(contest['startTimeSeconds']).strftime("%Y-%m-%dT%I:%M:%S-03:00"), 'endDate': datetime.datetime.fromtimestamp(contest['startTimeSeconds']+contest['durationSeconds']).strftime("%Y-%m-%dT%H:%M:%S-03:00")})
                else:
                    break
    return [flag, contests]

def main():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    codeforces_data = get_codeforces_contests()
    if codeforces_data[0] == True:
        for contest in codeforces_data[1]:
            event = {
                'event_id': '0'+str(contest['id']),
                'summary': contest['name'],
                'location': 'codeforces.com/contest/'+str(contest['id']),
                'description': 'Dia de subir rating no CF',
                'start': {
                    'dateTime': contest['startDate'],
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': contest['endDate'],
                    'timeZone': 'America/Sao_Paulo',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 12 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            print ('Event created: %s' % (event.get('htmlLink')))

if __name__ == '__main__':
    main()
