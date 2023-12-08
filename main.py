"""
This is the main script for running the telegram application. 
"""

from helpers.Prompter import Summarizer
import helpers.parsing as par
from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
import datetime, pytz, pickle, random
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

# For testing the connection
@client.on(events.NewMessage(incoming=True
                             , pattern=r'@kmsum23 chat_id'
                             ))
async def testing_handler(event):
    await event.reply(f"Chat id is {event.chat_id}")
    if not par.check_chat_id(id=event.chat_id, permissible_ids=permissible_ids):
        event.reply("This chat is not on the whitelist of permissible chat_id's")
    else:
        await event.reply("This chat is on the whitelist of permissible chat_id's")

# Just for fun ;)
@client.on(events.NewMessage(incoming=True
                             , pattern=r'.*deez nuts.*'
                             ))
async def summarization_handler(event):
    choices = [
        'LOL gottem'
        , 'LMAO gottem'
        , 'gottem'
    ]
    response = random.choice(choices)
    await event.reply(response)

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
    
    await event.reply("Sure let me try doing that for you.")

    # Otherwise carry on
    cutoff_time = par.obtain_cutoff_time(hours)
    # Obtain Messages, only obtain text / emoji messages for now
    messages = await par.obtain_messages(client=client, chat_id=event.chat_id, earliest_time=cutoff_time, text_only=True)
    
    # Perform the summarization
    await event.reply("Creating the summary . . . ")
    summarizer = Summarizer(messages=messages, model="gpt-3.5-turbo-1106")
    try:
        summary = await summarizer.summarize_simple()
        await event.reply(f"Summarized {len(messages)} Messages\n\n{summary}")
    except Exception as e:
        event.reply(f"Sorry, failed because of:\n\n{e}")



# To run the application
with client:
    # client.loop.run_until_complete(main())
    # print(f"Service is live\n\n")
    client.run_until_disconnected()
    # client.loop.run_until_complete(extract_messages(funemployment_id, None))