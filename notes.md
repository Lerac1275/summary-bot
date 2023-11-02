# Ideas

1. A bot that waits until about 10pm each day then sends a summary of the messages sent that day. 

2. Could also have a function where the user can interact with the bot (e.g. send a command) to get a quick summary of messages sent in the last X hour window(?)

# Implementation details
Will be built on the [python-telegram-bot API](https://docs.python-telegram-bot.org/en/stable/index.html). Will also have to use the openAI API to do the summarization. 

Can refer to the chatGPT generated information for a start. 

For the regular sending of the summary can look at [this utility](https://docs.python-telegram-bot.org/en/stable/telegram.ext.jobqueue.html) in the API. Otherwise there was another suggestion to have it [run as a CRON job](https://stackoverflow.com/questions/72156750/telegram-bot-to-send-auto-message-every-n-hours-with-python-telegram-bot). Second option not ideal, since I would also like the bot to be "listening" at all times for a user interaction (per idea #2). Will need to check with Rishabh how that might work when / if it reaches that stage. 

[Article](https://medium.com/analytics-vidhya/python-telegram-bot-with-scheduled-tasks-932edd61c534)