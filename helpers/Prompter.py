import re
import os, pickle
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.environ['openai_key']
from langchain.prompts import ChatPromptTemplate
from langchain.chat_models import ChatOpenAI


class Summarizer:
    def __init__(self, messages:list[dict], model:str='gpt-4', api_key = lambda x : openai_api_key):
        """
        Initialize the Summarizer instance. 

        Parameters
        ----------
        messages: list[dict]
            The list of messages to be summmarized. Each message is store in a dictionary containing the main message text along with other metadata (such as sender username etc).
        model: str, default "gpt-4"
            The LLM model to be used to the token generation. See more at https://platform.openai.com/docs/models/overview
        """
        self.model = model
        self.messages = messages
        self.api_key = api_key
        # For formatted messages. Left None for now. This should always be a list of dictionaries where each dictionary is the data on one message, in ascending order of time sent (most recent message should be the LAST element in the list) There should always be a 'names' key where the values are a list of possible names, and the first element is always the sender's username. 
        self.formatted_messages = None
        # For name mappings. Used to perform masking
        self.name_mappings = None
        # The chat string to be sent over to openai
        self.chat_string = None
    
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

        self.formatted_messages = formatted_messages

    # Make and store name mappings
    async def _make_name_mask(self):
        """
        Obtains the set of name-masking mappings and stores it as an attribute for use later on
        """
        try:
            unique_names = {tuple(x) for x in  map(lambda x: x['names'], self.formatted_messages)}
            # Will need to keep this to map back
            name_mappings = {f"name{i+1}":list(unique_names)[i] for i in range(len(unique_names))}
            self.name_mappings = name_mappings
        except TypeError as e:
            raise TypeError("self.formatted_messages is still None. Have you obtained any formatted messages yet?")

    # Construct the chat string in a simple manner
    async def _make_chat_string_simple(self):
        """
        Simple chat construction based on messages. Returns one chat string where each line is a chat message in the form <U>username</U>: message
        """
        chat_components = []
        for message in self.formatted_messages:
            # Recall that username will always be the FIRST element
            username = message['names'][0]
            message = message['message']
            comp = f"<U>{username}</U>: {message}"
            chat_components.append(comp)
        
        chat_string = "\n".join(chat_components)
        self.chat_string = chat_string

    async def _perform_mask(self, chat_string:str, outgoing=True):
        """
        Does the masking for a given string. Assumes that self.name_mappings has been populated already
        """

        if not self.name_mappings:
            raise Exception("self.name_mappings is still None. Call make_name_mask() to set it to the names for the given message set.")
        
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
    
    async def get_response(self, chat_string:str, example_input:str, example_response:str):
        system_message = """
        You will be given excerpts of messages from a group chat. 

        The name of the user who sent a message is between the <U> </U> tags. 

        Your task is to summarize the various conversations that took place in the group chat. For each conversation write a short summary of the points raised. 

        Split the final summary into smaller paragraphs of maximum 3 sentences each.
        """

        chat_template = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", "{example_input}"),
                ("ai", "{example_response}"),
                ("human", "{chat_string}"),
            ]
        )

        prompt = chat_template.format_messages(example_input = example_input, example_response=example_response, chat_string=chat_string)

        llm = ChatOpenAI(
            model_name = self.model
            , openai_api_key = (self.api_key)(0)
        )
    
        # Obtain the response
        response = llm(prompt)

        # Return the response
        try:
            return response.content
        
        except Exception as e:
            return e
        


    async def summarize_simple(self):
        """
        Summarizes the messages in a simple manner (no reply inclusion, no aggregating messages to a user), calls the helper _simple_ methods to do so
        """

        user_example = """
        <U>n1</U>: Wow the weather is really warm today
        <U>n1</U>: What are ya'll doing today pals. I'm going to cycling hohoho.
        <U>n2</U>: Ya sia today damn hot. Sweating like a dog bruh
        <U>n2</U>: Going out with my parents for lunch then watching a movie with YZ
        <U>n2</U>: WBU
        <U>n3</U>: Ya it's too hot already. I need the aircon. 
        <U>n3</U>: Man is going to study today. I got my final exam next week
        <U>n3</U>: Can't wait to go out hahaha
        <U>n3</U>: Lunch after finals pals?
        <U>n2</U>: Okay where u want eat
        <U>n1</U>: ATB for your exams @n3. You go this!
        <U>n1</U>: Ok sure we discuss after ur exams
        """

        ai_example = "Everyone agrees the weather is extremely warm.\n\nn1 is going to spend the day cycling, n2 is lunching with his parents then watching a movie with YZ, and n3 is studying for his final exams next week.\n\nn3 is looking forward to their exams ending, and everyone agrees to arrange a meal togehter once it ends."

        # format the messages
        await self._format_simple()

        # Set the masked names
        await self._make_name_mask()

        # Make the chat string
        await self._make_chat_string_simple()

        # Do name masking for outgoing text
        masked_chat_string = await self._perform_mask(self.chat_string, outgoing=True)

        # Obtain the response
        print("Obtaining Summary . . . ", end="")
        summary = await self.get_response(chat_string=masked_chat_string, example_input=user_example, example_response=ai_example)
        print("Done!")

        # Do the unmasking
        summary = await self._perform_mask(chat_string=summary, outgoing=False)

        # Return the summary
        return summary






    