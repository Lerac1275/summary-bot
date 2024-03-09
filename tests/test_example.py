import unittest
from helpers.Prompter import Summarizer
from helpers import parsing as par
from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
import datetime, pytz, pickle, random, asyncio
import pandas as pd
load_dotenv()

# Need to use a different base class for async functions. See: https://stackoverflow.com/a/59333941/13479945
class TestParser(unittest.IsolatedAsyncioTestCase):
    
    @classmethod
    def setUpClass(self):
        # Load Bot Token, api_id and api_hash
        self.bot_token, self.api_id, self.api_hash=os.environ.get("KevinMaloneBot_Token"), os.environ.get('api_id'), os.environ.get('api_hash')

        # Get the list of permissible chat_ids that can call this application
        self.permissible_ids = pd.read_csv("./data/chat_whitelist.csv")
        self.permissible_ids = self.permissible_ids.chat_id.values.tolist()

        # CLIENT WILL USE YOUR OWN TELEGRAM ACCOUNT
        self.client = TelegramClient('kmalone', api_id=self.api_id, api_hash=self.api_hash)

        print(f"Setup Complete")

    @classmethod
    def tearDownClass(self):
        pass

    async def test_firsttest(self):
        start_time = par.convert_to_utc("2023-12-20 00:00:00", 'Asia/Singapore')
        end_time = par.convert_to_utc("2023-12-20 23:59:59", 'Asia/Singapore')

        async with self.client:
            messages = await par.obtain_messages_time(client=self.client, chat_id=-1002048951454, earliest_time=start_time, latest_time=end_time)
        
        print(messages[:2])
        
        self.assertTrue(isinstance(messages, list))

            



    def test_second(self):
        self.assertEqual(2,2)

if __name__ == "__main__":
    unittest.main()

# Run all tests available in any directory anywhere by calling 
# python -m unittest discover
# From the command line