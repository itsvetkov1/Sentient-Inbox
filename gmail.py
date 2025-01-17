from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import os.path

# Define the scopes your app needs
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

def main():
    creds = None
    # Token storage
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If no valid credentials are available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Get the starred emails
    results = service.users().messages().list(
        userId='me',
        labelIds=['STARRED']
    ).execute()
    
    messages = results.get('messages', [])
    count = len(messages)

    with open('emails.txt', 'w', encoding='utf-8') as f:
        f.write(f'Number of starred emails: {count}\n\n')
        
        # Get and write details of all starred emails
        for message in messages:
            msg = service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()
            
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
            
            # Get email body
            if 'parts' in msg['payload']:
                parts = msg['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            body = part['body']['data']
                        elif 'attachmentId' in part['body']:
                            attachment = service.users().messages().attachments().get(
                                userId='me', messageId=message['id'],
                                id=part['body']['attachmentId']
                            ).execute()
                            body = attachment['data']
            else:
                body = msg['payload']['body'].get('data', '')

            # Decode body from base64 if it exists
            if body:
                import base64
                body = base64.urlsafe_b64decode(body).decode('utf-8')
            else:
                body = 'No body content available'
            
            f.write(f'From: {sender}\n')
            f.write(f'Subject: {subject}\n')
            f.write(f'Date: {date}\n')
            f.write(f'Body:\n{body}\n')
            f.write('-' * 50 + '\n\n')  # Add separator between emails

if __name__ == '__main__':
    main()
