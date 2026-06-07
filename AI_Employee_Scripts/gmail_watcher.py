import os
import logging
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from base_watcher import BaseWatcher

load_dotenv()

VAULT_PATH = os.getenv('VAULT_PATH', 'E:\\AI_Employee_Vault')
CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
DRY_RUN = os.getenv('DRY_RUN', 'true').lower() == 'true'

class GmailWatcher(BaseWatcher):
    def __init__(self):
        super().__init__(VAULT_PATH, check_interval=120)
        self.processed_ids = set()
        self.service = None
        self._setup_gmail()

    def _setup_gmail(self):
        try:
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            from google.auth.transport.requests import Request
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
            creds = None
            token_path = Path('token.json')

            if token_path.exists():
                creds = Credentials.from_authorized_user_file(
                    str(token_path), SCOPES
                )

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_PATH, SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                token_path.write_text(creds.to_json())

            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info('Gmail connected successfully!')

        except Exception as e:
            self.logger.error(f'Gmail setup failed: {e}')
            self.service = None

    def check_for_updates(self) -> list:
        if not self.service:
            self.logger.warning('Gmail not connected')
            return []

        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = [
                m for m in messages
                if m['id'] not in self.processed_ids
            ]
            self.logger.info(f'Found {len(new_messages)} new important emails')
            return new_messages

        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message) -> Path:
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            headers = {
                h['name']: h['value']
                for h in msg['payload']['headers']
            }

            sender = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            snippet = msg.get('snippet', '')

            if DRY_RUN:
                self.logger.info(
                    f'[DRY RUN] Would create action for email: {subject}'
                )

            content = f'''---
type: email
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
priority: high
status: pending
dry_run: {DRY_RUN}
---

## 📧 Email Received

**From:** {sender}
**Subject:** {subject}
**Received:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Preview
{snippet}

## Suggested Actions
- [ ] Read full email
- [ ] Draft reply (requires approval)
- [ ] Forward if needed (requires approval)
- [ ] Archive after processing

## Notes
*Add your notes here*
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content, encoding='utf-8')
            self.processed_ids.add(message['id'])
            self.logger.info(f'Created action file for email: {subject}')
            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            return None

if __name__ == '__main__':
    watcher = GmailWatcher()
    watcher.run()
