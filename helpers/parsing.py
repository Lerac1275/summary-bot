from telethon.sync import TelegramClient, events
from telethon.tl.custom.message import Message
import datetime, pytz, pickle, os, re, random

def get_joke_mappings():
    joke_mapping = {
        'deez nuts' : [
            'LOL gottem'
            , 'LMAO gottem'
            , 'GOTTEEEM'
        ]
        , "boolets" : [
            '🗣🗣🗣 I NEED MORE BOOOOOLLETS 🗣🗣🗣'
            , "Let's go to the gym buddy 💪💪"
        ]
        , "she said" : ['That\'s what she said 😗', 'That\'s what she said 😗', ""]

        , "shag" : ['It do be like that some times 😕', ""]
    }
    return joke_mapping

async def joke_replies(string:str):
    for k, v in get_joke_mappings().items():
        match = re.search(rf"{k}", string, flags=re.IGNORECASE)
        if match:
            return random.choice(v)
    
    return ""
    

# Checks the chat_id
def check_chat_id(id:int, permissible_ids:list[int]) -> bool:
    return id in permissible_ids
        
async def obtain_cutoff_time(n_hours:int, start_time:datetime.datetime=datetime.datetime.utcnow()) -> datetime.datetime:
    """
    Obtain the earliest time for retrieving messages based on the user input

    PARAMETERS
    ----------
    n_hours: int
        How many hours back to look from the startime
    start_time: datetime.datetime
        What the start time is for looking back. Needs to be in utc time
    
    RETURNS
    -------
    datetime.datetime

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

async def obtain_messages_last_n(client:TelegramClient, chat_id:int, n_messages:int, text_only = False) -> list[Message]:
    """
    Obtain the list of messages based on TIME, will return the actual message object. Note that the datetime attached to telethon Message objects are ALWAYS IN UTC.

    PARAMETERS
    ----------
    client: TelegramClient
        TelegramClient object used to make the API requests to obtain message objects
    chat_id:int
        The chat_id from which to retrieve the message
    text_only:bool
        Whether or not to filter for only messages that have some text (gifs / stickers / photos / videos have no text)
    
    RETURNS
    -------
    list[Message]
        A list of telethon Message objects
    """
    messages = []
    idx = 0 # is there a way to get iter() to work asynchronously?
    async for message in client.iter_messages(chat_id):
        idx +=1
        # Stop if the we have reached the no. of messages requested
        if idx > n_messages:
            break
        else:
            messages.append(message)
    
    if text_only:
        messages = list(filter(lambda x: not x.document, messages))

    return messages


async def obtain_messages_time(client:TelegramClient, chat_id:int, earliest_time:datetime.datetime, text_only:bool=False, latest_time:datetime.datetime=datetime.datetime.utcnow()) -> list[Message]:
    """
    Obtain the list of messages based on TIME, will return the actual message object. Note that the datetime attached to telethon Message objects are ALWAYS IN UTC.

    PARAMETERS
    ----------
    client: TelegramClient
        TelegramClient object used to make the API requests to obtain message objects
    chat_id:int
        The chat_id from which to retrieve the message
    earliest_time: datetime.datetime
        earliest possible datetime for a Message to be included. Will stop iterating backwards once a message is earlier than this time.
    text_only:bool
        Whether or not to filter for only messages that have some text (gifs / stickers / photos / videos have no text)
    latest_time : datetime.datetime
        When to start iterating backwards from
    
    RETURNS
    -------
    list[Message]
        A list of telethon Message objects
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

async def obtain_messages(client:TelegramClient, command_string:str, chat_id:int)-> list[Message]:
    """
    Main method used to obtain the chat messages for summarization. Currently supports two ways of retrieving messasges: last n hour(s) OR last n messages/msgs. This is the main method that calls the helper methods obtain_messages_time() OR obtain_messagse_last_n()

    PARAMETERS
    ----------
    client: TelegramClient
        TelegramClient object used to make the API requests to obtain message objects
    command_string:str
        The event message string that triggered the event handler in the application. Used to determine the retrival type to perform, and the number of messages / hours to use
    chat_id:int
        The chat_id from which to retrieve the message
    
    RETURNS
    -------
    list[Message]
        A list of telethon Message objects
    """
    # Obtain the number & whether it's hours or messages
    try:
        n, type = re.search(r"(\d+) (messages|msgs|hours{0,1})", command_string).groups()
        n = int(n)
    except Exception as e:
        return e
    # Obtain messages based on last n hours
    if "hour" in type:
        cutoff_time = await obtain_cutoff_time(n_hours=n)
        messages = await obtain_messages_time(client=client, chat_id=chat_id, earliest_time=cutoff_time, text_only=True)
    
    # Obtain messages based on last n messages
    else:
        messages = await obtain_messages_last_n(client=client, chat_id=chat_id, n_messages=n, text_only=False)
    
    return messages
