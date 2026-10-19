import os
from pathlib import Path

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from carlobot import config


class SheetAuthenticator:
    def _authenticate_oauth(self):
        creds = None
        token_path = config.TOKEN_PATH
        # Check token path
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(
                str(token_path), config.SCOPES
            )
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except RefreshError:
                    if token_path.exists():
                        token_path.unlink()
                    creds = None

            if not creds or not creds.valid:
                client_secrets = config.BASE_DIR / "credentials.json"
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(client_secrets), config.SCOPES
                )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(token_path, "w") as token:
                token.write(creds.to_json())

        return creds

    def _authenticate_service_account(self):
        creds = service_account.Credentials.from_service_account_file(
            config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=config.SCOPES
        )

        return creds

    def authenticate(self):
        return self._authenticate_service_account()
