"""
This is the main script for running the telegram application. 
"""

from helpers.Prompter import Summarizer
import helpers.parsing as par
from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
import datetime, pytz, pickle
import pandas as pd
load_dotenv()

# Load Bot Token, api_id and api_hash
bot_token, api_id, api_hash=os.environ.get("KevinMaloneBot_Token"), os.environ.get('api_id'), os.environ.get('api_hash')

# Get the list of permissible chat_ids that can call this application
permissible_ids = pd.read_csv("./data/chat_whitelist.csv")
permissible_ids = permissible_ids.chat_id.values.tolist()

# CLIENT WILL USE YOUR OWN TELEGRAM ACCOUNT
client = TelegramClient('kmalone', api_id=api_id, api_hash=api_hash)

# For testing the connection
@client.on(events.NewMessage(incoming=True
                             , pattern=r'^test$'
                             ))
async def testing_handler(event):
    print(f"EVENT TRIGGERED\n\n{event.stringify()}\n\n")
    print(f"MESSAGE:\n{event.message.stringify()}")
    print(f"\nThis was from chat Id {event.chat_id}")
    await event.reply('Test')

# Handle the command to summarize
@client.on(events.NewMessage(incoming=True
                             , pattern=r'^@kmsum23 summarize.*'
                             ))
async def summarization_handler(event):
    print(f"EVENT TRIGGERED\n\n{event.stringify()}\n\n")
    print(f"MESSAGE:\n{event.message.stringify()}")
    print(f"\nThis was from chat Id {event.chat_id}")

    # Check that this was from a valid chat_id
    if not par.check_chat_id(id=event.chat_id, permissible_ids=permissible_ids):
        await event.reply("You cannot call this program from this chat.")
        return
    
    # Otherwise obtain the cutoff time
    hours = par.obtain_hours(event.message.message)
    # If no hours found then reply 
    if not hours:
        await event.reply("No Hours Specified")
        return
    
    # Otherwise carry on
    cutoff_time = par.obtain_cutoff_time(hours)
    # Obtain Messages, only obtain text / emoji messages for now
    messages = await par.obtain_messages(client=client, chat_id=event.chat_id, cutoff_time=cutoff_time, text_only=True)
    # Format messages
    messages = await par.format_messages(messages=messages)

    

    await event.reply('Summarization Placeholder')


# To run the application
with client:
    # client.loop.run_until_complete(main())
    # print(f"Service is live\n\n")
    client.run_until_disconnected()
    # client.loop.run_until_complete(extract_messages(funemployment_id, None))