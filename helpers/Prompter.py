

class Summarizer:
    def __init__(self, messages:list[dict], model:str='gpt-4'):
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

        

    def summarize(self):
        """
        Summarizes the messages per a default prompt
        """


    