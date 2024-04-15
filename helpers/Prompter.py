import re
import os, pickle
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.environ['openai_key']
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI
from pprint import pprint

class Summarizer:
    def __init__(self, messages:list[dict]
                #  , model:str="gpt-3.5-turbo"
                 , model:str="gpt-4-1106-preview"
                 , api_key = lambda x : openai_api_key):
        """
        Initialize the Summarizer instance. This is the class object used to store message objects, format them & obtain the summary from openai. Masking is also performed to conceal user sender identities. 


        Parameters
        ----------
        messages: list[dict]
            The list of messages to be summmarized. Each message is store in a dictionary containing the main message text along with other metadata (such as sender username etc).
        model: str, default "gpt-4"
            The LLM model to be used to the token generation. See more at https://platform.openai.com/docs/models/overview
        api_key: function
            A function that returns the api_key given any input.
        """
        self.model = model
        self.messages = messages
        self.api_key = api_key
        # For formatted messages. Left None for now. This should always be a list of dictionaries where each dictionary is the data on one message, in ascending order of time sent (most recent message should be the LAST element in the list) There should always be a 'names' key where the values are a list of possible names, and the first element is always the sender's username. 
        self.formatted_messages = None
        # For name mappings. Used to perform masking
        self.name_mappings = None
    
    # Simple info. extraction from message list
    async def _format_simple(self) -> list[dict]:
        """
        Formats the messages in a simple manner. Each message is self.messages has the following information extracted from it:
        
        msg = {
            'names' : list[str], list of [username, first_name, last_name] of the message sender
            , 'replied_message': str, the message text this message was replying to, None if not a reply
            , 'message':str, the text of this message
        }
        """
        formatted_messages = []

        # Order from latest to newest (most recent last)
        for message in self.messages[::-1]:
            
            # Get all possible names of the user, filtering for None values
            msg_sender_names = await message.get_sender()
            # Is this the self (i.e the same account as the application)
            is_self = msg_sender_names.is_self
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
                , 'is_self':is_self
            }
            
            # Store        
            formatted_messages.append(msg)


        self.formatted_messages = formatted_messages

    # Make and store name mappings
    async def _make_name_mask(self, prefix="name"):
        """
        Obtains the set of name-masking mappings and stores it as an attribute for use later on
        """
        try:
            unique_names = {tuple(x) for x in  map(lambda x: x['names'], self.formatted_messages)}
            # Will need to keep this to map back
            name_mappings = {f"{prefix}{i+1}":list(unique_names)[i] for i in range(len(unique_names))}
            self.name_mappings = name_mappings
        except TypeError as e:
            raise TypeError("self.formatted_messages is still None. Have you obtained any formatted messages yet?")

    # Construct the summarizer string in a simple manner
    async def _make_summarizer_string_simple(self, formatted_msgs = None):
        """
        Simple chat construction based on messages. Returns one chat string where each line is a chat message in the form <U>username</U>: message
        """
        chat_components = []
        if not formatted_msgs:
            formatted_msgs = self.formatted_messages
        
        for message in formatted_msgs:
            # Recall that username will always be the FIRST element
            username = message['names'][0]
            message = message['message']
            comp = f"<U>{username}</U>: {message}"
            chat_components.append(comp)
        
        chat_string = "\n".join(chat_components)
        return chat_string

    async def _make_chat_message_list(self):
        """
        Goes through the formatted messages and constructs the a chat message list of the form 
        [
            ('human', <human message>)
            , ('ai', <ai message>)
            , ('human', <human message>)
            , ('ai', <ai message>)
            , . . . 
        ]
        
        It is possible to have multiple ('human', ...) messages in the list
        
        """
        chat_message_list = []
        for message in self.formatted_messages:
            if message['is_self']:
                chat_message_list.append(('ai', message['message']))
            else:
                # Remove the tag in the prompt message
                prompt=re.sub("^@kmsum23", "", message['message'])
                chat_message_list.append(('human', prompt))

        return chat_message_list






    async def _perform_mask(self, chat_string:str, outgoing=True):
        """
        Does the masking for a given string. Assumes that self.name_mappings has been populated already
        """

        if not self.name_mappings:
            raise Exception(f"self.name_mappings is {self.name_mappings}. Call make_name_mask() to set it to the names for the given message set.")
        
        # If this is for an OUTGOING chat string (being sent to the api)
        if outgoing:
            # Will be replacing the items (username / first_name / last_name) with the KEY (name placeholder)
            for masked_name, v in self.name_mappings.items():
                for name in v:
                    chat_string = re.sub(fr"\b{name}\b", masked_name, chat_string, flags=re.IGNORECASE)

        else:
            # Otherwise do the reverse
            for masked_name, names in self.name_mappings.items():
                username = names[0]
                chat_string = re.sub(fr"\b{masked_name}\b", username, chat_string, flags=re.IGNORECASE)
        
        return chat_string
    
    async def get_response(self, message_list):
        # print(message_list, "\n<END OF MESSAGE LIST>")
        chat_template = ChatPromptTemplate.from_messages(
            message_list
        )

        prompt = chat_template.format_messages()
        llm = ChatOpenAI(
            model_name = self.model
            , openai_api_key = (self.api_key)(0)
        )
    
        try:
            # Obtain the response
            response = llm(prompt)
            # Return the response
            print('Response Received\n')
            return response.content
        
        except Exception as e:
            print(e)
            return e
        


    async def summarize_simple(self):
        """
        Summarizes the messages in a simple manner (no reply inclusion, no aggregating messages to a user), calls the helper _simple_ methods to do so
        """

        system_message = """
        You will be given excerpts of messages from a group chat. 

        The name of the user who sent a message is between the <U> </U> tags. 

        Your task is to summarize the various conversations that took place in the group chat. For each conversation write a short summary of the points raised. 

        Split the final summary into smaller paragraphs of maximum 3 sentences each.
        """

        user_example = """
        <U>name1</U>: Wow the weather is really warm today
        <U>name1</U>: What are ya'll doing today pals. I'm going to cycling hohoho.
        <U>name2</U>: Ya sia today damn hot. Sweating like a dog bruh
        <U>name2</U>: Going out with my parents for lunch then watching a movie with YZ
        <U>name2</U>: WBU
        <U>name3</U>: Ya it's too hot already. I need the aircon. 
        <U>name3</U>: Man is going to study today. I got my final exam next week
        <U>name3</U>: Can't wait to go out hahaha
        <U>name3</U>: Lunch after finals pals?
        <U>name2</U>: Okay where u want eat
        <U>name1</U>: ATB for your exams @n3. You go this!
        <U>name1</U>: Ok sure we discuss after ur exams
        """

        ai_example = "Everyone agrees the weather is extremely warm."\
                    "\n\nname1 is going to spend the day cycling, name2 is lunching with his parents then watching a movie with YZ, and name3 is studying for his final exams next week."\
                    "\n\nname3 is looking forward to their exams ending, and everyone agrees to arrange a meal togehter once it ends."

        # format the messages
        await self._format_simple()
        

        # Set the masked names
        await self._make_name_mask()

        # Make the chat string
        chat_string = await self._make_summarizer_string_simple()
        # print(f"chat String: {chat_string}\n<END OF CHAT_STRING>\n")

        # Do name masking for outgoing text
        masked_chat_string = await self._perform_mask(chat_string, outgoing=True)
        # print(f"masked_chat_string: {masked_chat_string}\n <END OF MASKED CHAT STRING>\n")
        # Obtain the response
        print("Obtaining Summary . . . ")
        message_list = [
                ("system", f"{system_message}"),
                ("human", f"{user_example}"),
                ("ai", f"{ai_example}"),
                ("human", f"Ignore the previous messages and summarize just these now:\n\n{masked_chat_string}"),
            ]
        summary = await self.get_response(message_list)
        print("Done!")

        # Do the unmasking
        summary = await self._perform_mask(chat_string=summary, outgoing=False)

        # Return the summary
        return summary
    
    async def chat_simple(self):
        """
        Construct the chat thread chain and obtain the chat response
        """

        system_message = f"You are a chatbot embedded in a group chat. Your purpose is to answer questions the group members may have."\
                        f"\nIf you feel you don't have enough context of the group chat to answer, just try your best. Otherwise just reply with a 🤷‍♂️"\
                        f"\nSplit your response into paragraphs of not more than 3 sentences each."\

        # format the messages. This will make the last message in self.formatted_messages the MOST RECENT ONE
        await self._format_simple()

        # Set the masked names
        await self._make_name_mask()

        # Construct the chat string
        chat_message_list = await self._make_chat_message_list()

        # Do name masking for outgoing text
        masked_message_list = []
        for msg in chat_message_list:
            type, text = msg
            text = await self._perform_mask(text, outgoing=True)
            masked_message_list.append((type, text))

        # Add the system message
        masked_message_list = [('system', system_message)] + masked_message_list
        pprint(masked_message_list[1:]) # Ignore system message
        
        # Get the API response
        response = await self.get_response(masked_message_list)

        # Do the unmasking
        response = await self._perform_mask(chat_string=response, outgoing=False)

        return response










    