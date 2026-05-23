import os
import csv
import os.path
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
import base64
from bs4 import BeautifulSoup

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me").execute()
    messages = results.get("messages", [])
    service.close()
    if not messages:
      print("No labels found.")
      return
    print("messages:")
    for message in messages:
      #print(message['threadId'])
      pass

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except:
            os.remove('token.json')
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# --- Extract URLs from Email Body ---
def extract_urls(text):
    """Extract all URLs from text using regex."""
    url_pattern = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    return url_pattern.findall(text)

def get_email_body(service, msg_id):
    """Fetch and decode email body (plain text or HTML)."""
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
            elif part['mimeType'] == 'text/html':
                html = part['body']['data']
                soup = BeautifulSoup(base64.urlsafe_b64decode(html).decode('utf-8'), 'html.parser')
                body = soup.get_text()
                break
    else:
        body = message['payload']['body']['data']

    return base64.urlsafe_b64decode(body).decode('utf-8') if body else ''

def get_email_details(service, msg_id):
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = message['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

    # Extract and parse the received date
    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
    try:
        # Parse RFC 2822 date format (e.g., "Mon, 21 May 2026 14:30:00 +0300")
        date = parsedate_to_datetime(date_str)
        # Format as readable string (adjust timezone as needed)
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S %Z')  # e.g., "2026-05-21 14:30:00 +0300"
    except:
        formatted_date = date_str  # Fallback to raw string

    # Extract body
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
            elif part['mimeType'] == 'text/html':
                html = part['body']['data']
                soup = BeautifulSoup(base64.urlsafe_b64decode(html).decode('utf-8'), 'html.parser')
                body = soup.get_text()
                break
    else:
        body = message['payload']['body']['data']

    body = base64.urlsafe_b64decode(body).decode('utf-8') if body else ''
    urls = extract_urls(body)

    return {
        'subject': subject,
        'sender': sender,
        'date': formatted_date,
        'urls': urls
    }

# --- Search Emails ---
def search_emails(service, query, max_results=10):
    """Search emails using Gmail's query syntax.
    Example queries:
    - 'from:amazon@orders.com subject:receipt'
    - 'subject:"Your invoice"'
    - 'from:no-reply@github.com'
    """
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    return results.get('messages', [])

def get_email_details(service, msg_id):
    message = service.users().messages().get(
        userId='me',
        id=msg_id,
        format='full'
    ).execute()

    headers = message['payload']['headers']
    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

    # Extract and parse the received date
    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
    try:
        # Parse RFC 2822 date format (e.g., "Mon, 21 May 2026 14:30:00 +0300")
        date = parsedate_to_datetime(date_str)
        # Format as readable string (adjust timezone as needed)
        formatted_date = date.strftime('%Y-%m-%d %H:%M:%S %Z')  # e.g., "2026-05-21 14:30:00 +0300"
    except:
        formatted_date = date_str  # Fallback to raw string

    # Extract body
    body = ''
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain':
                body = part['body']['data']
                break
            elif part['mimeType'] == 'text/html':
                html = part['body']['data']
                soup = BeautifulSoup(base64.urlsafe_b64decode(html).decode('utf-8'), 'html.parser')
                body = soup.get_text()
                break
    else:
        body = message['payload']['body']['data']

    body = base64.urlsafe_b64decode(body).decode('utf-8') if body else ''
    urls = extract_urls(body)

    return {
        'subject': subject,
        'sender': sender,
        'date': formatted_date,
        'urls': urls
    }

# --- Main Workflow ---
def scan_emails(service, query='is:unread', max_results=10):
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    messages = results.get('messages', [])

    message_list = []
    for msg in messages:
        details = get_email_details(service, msg['id'])
        #print(f"Subject: {details['subject']}")
        #print(f"From: {details['sender']}")
        #print(f"Received: {details['date']}")
        #print(f"URL: {details['urls'][0]}")
        #details['status'] = 'new'
        message_list.append(details)

        #print(details)
    #print(message_list)
    #Write message list to csv
    fieldnames = ['subject','sender','date','urls','status']

    #listings.csv is always overwritten
    with open('listings.csv', mode ='w', newline = '') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(message_list)
    

    #Add status as new to each row


if __name__ == '__main__':
    service = get_gmail_service()
    scan_emails(service, query='from:etuovi.com')  # 🔍 Customize query
    print("Mail Scan completed")