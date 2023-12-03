# docs: https://docs.telethon.dev/en/stable/index.html

from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
import datetime, pytz, pickle
load_dotenv()
# Load Bot Token, api_id and api_hash
bot_token, api_id, api_hash=os.environ.get("KevinMaloneBot_Token"), os.environ.get('api_id'), os.environ.get('api_hash')

# Chat ID for my test group chat
test_chat_id = -4020519896
# Chat ID for funemployment
funemployment_id = -1002060073951

# Gets messages from a specific chatid up to a certain cutoff time.
async def get_messages(chat_id, cutoff_time):
    # Just a placeholder fornow, will need to abstract this away to a function that computes the cutoff time when given a user instruction
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=8)
    # Create a timezone object for UTC
    utc_timezone = pytz.timezone('UTC')
    # Make the datetime object aware of the UTC timezone
    cutoff_time = utc_timezone.localize(cutoff_time)

    messages = []
    async for message in client.iter_messages(chat_id):
        # print(message.message, message.date)
        if message.date < cutoff_time:
            break
        else:
            messages.append(message)

    # View from first to last
    for message in messages[::-1]:
        # Get the username of the sender
        msg_sender = await message.get_sender()
        msg_sender = msg_sender.username
        # Pring message details
        print(f"Message sent at: {message.date}\nMessage Sender: {msg_sender}\nMessage: {message.message}\n\n")
    pass

# Temp function to extract chat messages for tesitng in LLM summarization piece
async def extract_messages(chat_id, cutoff_time):
    # Just a placeholder fornow, will need to abstract this away to a function that computes the cutoff time when given a user instruction
    cutoff_time = datetime.datetime.utcnow() - datetime.timedelta(hours=12)
    # Create a timezone object for UTC
    utc_timezone = pytz.timezone('UTC')
    # Make the datetime object aware of the UTC timezone
    cutoff_time = utc_timezone.localize(cutoff_time)

    messages = []
    async for message in client.iter_messages(chat_id):
        # print(message.message, message.date)
        if message.date < cutoff_time:
            break
        else:
            # Get the username of the sender
            msg_sender = await message.get_sender()
            msg_sender = msg_sender.username
            
            msg= {
                'sender': msg_sender
                , 'datetime':message.date
                , 'message':message.message
            }
            messages.append(msg)

    with open('sample_messages.pkl', 'wb') as file:
        pickle.dump(messages, file)
    pass


##############################
# TEST OUT THE CLIENT MEHTOD #
##############################
# CLIENT WILL USE YOUR OWN TELEGRAM ACCOUNT
client = TelegramClient('kmalone', api_id=api_id, api_hash=api_hash)


@client.on(events.NewMessage(incoming=True
                             , pattern=r'@kmsum23 summarize.*'
                             ))
async def my_event_handler(event):
    print(f"EVENT TRIGGERED\n\n{event.stringify()}\n\n")
    print(f"MESSAGE:\n{event.message.stringify()}")
    print(f"\nThis was from chat Id {event.chat_id}")

    await event.reply('Summarization Placeholder')

# This works for TelegramClients using real accounts (not bots)
async def main():
    # Getting information about yourself
    me = await client.get_me()

    # "me" is a user object. Pretty print
    # print(me.stringify())

    # Account metadata
    username = me.username
    print(f"Username: {username}\n")
    print(f"Phone Number: {me.phone}\n")

    # You can print all the dialogs/conversations that you are part of:
    async for dialog in client.iter_dialogs():
        print(dialog.name, 'has ID:', dialog.id)

    

    # Printing message details for a group
    # funemployment_id = -1002060073951
    # # Get the group entity
    # group = await client.get_entity(funemployment_id)
    # idx = 0
    # async for message in client.iter_messages(group, min_id=1):
    #     idx +=1
    #     if idx > 100:
    #         break
    #     print(message.date, message.text)




    # These won't work and will return an error as the correct receiver ID has not been specified
    # # ...to some chat ID
    # await client.send_message(-100123456, 'Hello, group!')
    # # ...to your contacts
    # await client.send_message('+34600123123', 'Hello, friend!')
    # # ...or even to any username
    # await client.send_message('username', 'Testing Telethon!')

    # # You can, of course, use markdown in your messages:
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and '
    #     'a [nice website](https://example.com)!',
    #     link_preview=False
    # )

    # # Sending a message returns the sent message object, which you can use
    # print(message.raw_text)

    # # You can reply to messages directly if you have a message object
    # await message.reply('Cool!')

    # # Or send files, songs, documents, albums...
    # await client.send_file('me', '/home/me/Pictures/holidays.jpg')

    # # You can print the message history of any chat:
    # async for message in client.iter_messages('me'):
    #     print(message.id, message.text)

    #     # You can download media from messages, too!
    #     # The method will return the path where the file was saved.
    #     if message.photo:
    #         path = await message.download_media()
    #         print('File saved to', path)  # printed after download is done

with client:
    # client.loop.run_until_complete(main())
    # print(f"Service is live\n\n")
    # client.run_until_disconnected()
    client.loop.run_until_complete(extract_messages(funemployment_id, None))

