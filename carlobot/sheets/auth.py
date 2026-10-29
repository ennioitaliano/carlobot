from google.oauth2 import service_account

from carlobot import config


class SheetAuthenticator:
    def authenticate(self) -> service_account.Credentials:
        return service_account.Credentials.from_service_account_file(
            config.GOOGLE_SERVICE_ACCOUNT_FILE, scopes=config.SCOPES
        )
