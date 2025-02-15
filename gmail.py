from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from typing import Dict, List, Optional
import os.path
import base64
import logging

logger = logging.getLogger(__name__)

# Define the scopes your app needs
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

class GmailClient:
    """Gmail API client for email operations."""
    
    def __init__(self):
        self.service = self._authenticate()
        
    def _authenticate(self):
        """Authenticate with Gmail API."""
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

        return build('gmail', 'v1', credentials=creds)
        
    def _extract_email_parts(self, msg: Dict) -> Dict[str, str]:
        """Extract email body and attachments."""
        body = ""
        
        if 'parts' in msg['payload']:
            parts = msg['payload']['parts']
            for part in parts:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = part['body']['data']
                    elif 'attachmentId' in part['body']:
                        attachment = self.service.users().messages().attachments().get(
                            userId='me',
                            messageId=msg['id'],
                            id=part['body']['attachmentId']
                        ).execute()
                        body = attachment['data']
        else:
            body = msg['payload']['body'].get('data', '')

        # Decode body from base64 if it exists
        if body:
            try:
                body = base64.urlsafe_b64decode(body).decode('utf-8')
            except Exception as e:
                logger.error(f"Error decoding email body: {e}")
                body = 'Error decoding content'
        else:
            body = 'No content available'
            
        return body
        
    def _extract_recipients(self, headers: List[Dict]) -> List[str]:
        """Extract all recipients from email headers."""
        recipients = []
        recipient_fields = ['To', 'Cc', 'Bcc']
        
        for field in recipient_fields:
            value = next((h['value'] for h in headers if h['name'] == field), '')
            if value:
                # Split and clean email addresses
                addresses = [addr.strip() for addr in value.split(',')]
                recipients.extend(addresses)
                
        return recipients
        
    def _get_thread_messages(self, thread_id: str) -> List[str]:
        """Get all message IDs in a thread."""
        try:
            thread = self.service.users().threads().get(
                userId='me',
                id=thread_id
            ).execute()
            
            return [msg['id'] for msg in thread['messages']]
        except Exception as e:
            logger.error(f"Error getting thread messages: {e}")
            return []

    def get_unread_emails(self, max_results: int = 50) -> List[Dict]:
        """
        Get unread emails with thread information.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email data dictionaries
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                labelIds=['UNREAD'],
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for message in messages:
                try:
                    # Get full message data
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()

                    headers = msg['payload']['headers']
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
                    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
                    
                    # Get thread information
                    thread_id = msg.get('threadId', '')
                    thread_messages = self._get_thread_messages(thread_id) if thread_id else []
                    
                    # Get all recipients
                    recipients = self._extract_recipients(headers)
                    
                    # Get message content
                    body = self._extract_email_parts(msg)

                    email_data = {
                        "message_id": message['id'],
                        "thread_id": thread_id,
                        "thread_messages": thread_messages,
                        "subject": subject,
                        "sender": sender,
                        "recipients": recipients,
                        "received_at": date,
                        "content": body
                    }
                    
                    emails.append(email_data)
                    
                except Exception as e:
                    logger.error(f"Error processing message {message['id']}: {e}")
                    continue

            return emails

        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            return []

    def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking message {message_id} as read: {e}")
            return False

    def mark_as_unread(self, message_id: str) -> bool:
        """Mark a message as unread."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return True
        except Exception as e:
            logger.error(f"Error marking message {message_id} as unread: {e}")
            return False
