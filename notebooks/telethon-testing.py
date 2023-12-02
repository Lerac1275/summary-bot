# docs: https://docs.telethon.dev/en/stable/index.html

from telethon.sync import TelegramClient, events
from dotenv import load_dotenv
import os
load_dotenv()
# Load Bot Token, api_id and api_hash
bot_token, api_id, api_hash=os.environ.get("KevinMaloneBot_Token"), os.environ.get('api_id'), os.environ.get('api_hash')

##############################
# TEST OUT THE CLIENT MEHTOD #
##############################
# CLIENT WILL USE YOUR OWN TELEGRAM ACCOUNT
client = TelegramClient('kmalone', api_id=api_id, api_hash=api_hash)


@client.on(events.NewMessage)
async def my_event_handler(event):
    if 'hello' in event.raw_text:
        await event.reply('hi!')

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
        print(dialog.name, 'has ID', dialog.id)

    

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
    client.loop.run_until_complete(main())
    client.run_until_disconnected()

