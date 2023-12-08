from telethon.sync import TelegramClient, events
from telethon.tl.custom.message import Message
import datetime, pytz, pickle, os, re

# Checks the chat_id
def check_chat_id(id:int, permissible_ids:list[int]) -> bool:
    return id in permissible_ids
    

def obtain_hours(msg:str) -> int:
    """
    Returns the number of hours to retrieve messages for
    """
    pattern = r'last (\d+) hour'
    match = re.search(pattern, msg)
    if match:
        hours = int(match.group(1))
        return hours
    else:
        return None
    
def obtain_cutoff_time(n_hours:int, start_time:datetime.datetime=datetime.datetime.utcnow()) -> datetime.datetime:
    """
    Obtain the cutoff time for retrieving messages
    """
    try:
        cutoff_time = start_time - datetime.timedelta(hours=n_hours)
    except TypeError as e:
        print(f"{e}\n\nExpected an integer")
    # Create a timezone object for UTC
    utc_timezone = pytz.timezone('UTC')
    try:
        # Make the datetime object aware of the UTC timezone
        cutoff_time = utc_timezone.localize(cutoff_time)
    except ValueError as e:
        None
    return cutoff_time

async def obtain_messages(client:TelegramClient, chat_id:int, earliest_time:datetime.datetime, text_only:bool=False, latest_time:datetime.datetime=datetime.datetime.utcnow()) -> list[Message]:
    """
    Obtain the list of messages, will return the actual message object
    """
    messages = []
    async for message in client.iter_messages(chat_id, offset_date=latest_time):
        # Stop if the we have reached messages th
        if message.date < earliest_time:
            break
        else:
            messages.append(message)
    
    if text_only:
        messages = list(filter(lambda x: not x.document, messages))

    return messages

async def construct_chat_simple(messages:dict):
    """
    Simple chat construction based on messages. Returns one chat string where each line is a chat message in the form <U>username</U>: message
    """
    chat_components = []
    for message in messages:
        username = message['names'][0]
        message = message['message']
        comp = f"<U>{username}</U>: {message}"
        chat_components.append(comp)
    return chat_components
