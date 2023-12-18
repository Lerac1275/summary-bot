"""
This is the main script for running the telegram application. 
"""

from helpers.Prompter import Summarizer
import helpers.parsing as par
from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
import datetime, pytz, pickle, random, asyncio
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
                             , func=par.joke_filter))
async def summarization_handler(event):
    print(f"Joke at {datetime.datetime.utcnow()}\n")
    response = await par.joke_replies(event.message.message)
    if response:
        await asyncio.sleep(1)
        await event.reply(response)
    else:
        return

# Handle the command to summarize
@client.on(events.NewMessage(incoming=True
                             , pattern=r'^@kmsum23 summarize last.*'
                             ))
async def summarization_handler(event):
    print(f"EVENT TRIGGERED\n\n{event.stringify()}\n\n")
    print(f"MESSAGE:\n{event.message.stringify()}")
    print(f"\nThis was from chat Id {event.chat_id}")

    # Check that this was from a valid chat_id
    if not par.check_chat_id(id=event.chat_id, permissible_ids=permissible_ids):
        await event.reply("You cannot call this program from this chat.")
        return
    
    messages = await par.obtain_messages_summary(client=client, command_string=event.message.message, chat_id=event.chat_id)

    # Need to tidy up this error handling
    if isinstance(messages, Exception): # if the message obtainment failed for whatever reason
        if isinstance(messages, AttributeError):
            await event.reply(f"Message loading failed, likely because your command does not match the recognized format.")
        else:
            await event.reply(f"Message loading failed due to:\n\n{messages}")
        return
    elif len(messages) == 0:
        await event.reply(f"No messages dedected for the specified window. Nothing to summarize")
        return
    
    
    await event.reply("Sure let me try doing that for you.")
    
    # Perform the summarization
    await event.reply("Creating the summary . . . ")
    summarizer = Summarizer(messages=messages, model="gpt-3.5-turbo-1106")
    try:
        summary = await summarizer.summarize_simple()
        await event.reply(f"Summarized {len(messages)} Messages at {event.message.date}\n\n{summary}")
        # Not sure if this is really needed or if garbage collection will handle this
        del summarizer
        del messages
    except Exception as e:
       await event.reply(f"Sorry, failed because of:\n\n{e}")


# Handle the command to chat
@client.on(events.NewMessage(incoming=True
                             , pattern=r'^@kmsum23 chat.+'
                             ))
async def chat_handler(event):
    try:
        messages = await par.obtain_messages_chat(client=client, chat_msg=event.message)
        chat_obj = Summarizer(messages=messages)
        print("obtained_msgs")
        response = await chat_obj.chat_simple()
        print(f"obtained response:\n{response}")
        await event.reply(response)
    except Exception as e:
        await event.reply(f"Failed to generate response due to:\n\n{e}")
    pass


# To run the application
with client:
    print("Application is live")
    # client.loop.run_until_complete(main())
    # print(f"Service is live\n\n")
    client.run_until_disconnected()
    # client.loop.run_until_complete(extract_messages(funemployment_id, None))