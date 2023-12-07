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

async def obtain_messages(client:TelegramClient, chat_id:int, cutoff_time:datetime.datetime, text_only:bool=False) -> list[Message]:
    """
    Obtain the list of messages, will return the actual message object
    """
    messages = []
    async for message in client.iter_messages(chat_id):
        # print(message.message, message.date)
        if message.date < cutoff_time:
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
    async for message in messages:
        username = message['names'][0]
        message = message['message']
        comp = f"<U>{username}</U>: {message}"
        chat_components.append(comp)
    return chat_components

async def format_messages(messages:list[Message]) -> str:
    """
    Formats the inputted telethon Message Objects to the desired format for passing to the summarization object.
    """
    formatted_messages = []

    # Order from latest to newest (most recent last)
    for message in messages[::-1]:
        
        # Get all possible names of the user, filtering for None values
        msg_sender_names = await message.get_sender()
        # Note that the username will ALWAYS be populated, and is the first element of this list
        msg_sender_names = list(filter(lambda x: x, [msg_sender_names.username, msg_sender_names.first_name, msg_sender_names.last_name]))
        
        # If this message was a reply to another message, get the message it text it was replying
        if message.is_reply:
            replied_msg = await message.get_reply_message()
            replied_msg = replied_msg.message
        else:
            replied_msg=None

        # Data on this message
        msg = {
            'names' : msg_sender_names
            , 'replied_message':replied_msg
            , 'message':message.message
        }
        
        # Store        
        formatted_messages.append(msg)
    
    # Construct the chat string
    chat_string = await construct_chat_simple(formatted_messages)
    chat_string = "\n".join(chat_string)
    
    # NAME MASKING SECTION. SHOULD BE ABSTRACTED OUT 
    unique_names = {tuple(x) for x in  map(lambda x: x['names'], formatted_messages)}
    # Will need to keep this to map back
    name_mappings = {f"name{i+1}":list(unique_names)[i] for i in range(len(unique_names))}
    for k, v in name_mappings.items():
        for name in v:
            chat_string = re.sub(fr"{name}", k, chat_string, flags=re.IGNORECASE)
    # Outgoing chat string is now masked


    return chat_string