from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
load_dotenv()

api_id = os.getenv('tg_app_id')
api_hash = os.getenv('tg_api_hash')

class TelegramScraper:
    def __init__(self, api_id, api_hash, phone_number, session_name):
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone_number = phone_number
        self.session_name = session_name
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
