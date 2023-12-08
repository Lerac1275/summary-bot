# Introduction

The goal of this project is to create a telegram bot that can summarize group chat messages on command. 

A user would be able to specify that they'd like a quick summary of messages from the last X hours, the bot would do its thing and return a short passage about the main topics being discussed. This was to be a simple solution to the problem of opening up a group chat and seeing 200 undread messages. 

# To Run
To run this you will need to have several things:

1. A telegram application id & hash. See more [here](https://docs.telethon.dev/en/stable/index.html)

2. An telegram account (**not** a bot). See [notes](./notes.md) for more background.
    -   The first time the application is run, you will be prompted to enter the number of the account, then key in an OTP. A `.session` object will be created so you will not need to repeat this in the future. 

3. The name & `chat_id` of the group chat you want to be able to use this application in must have been added to `chat_whitelist.csv`
    - Once the application account is added to the group you may obtain the `chat_id` by messaging `@kmsum23 chat_id` when the application is running.
    - Add it to `chat_whitelist.csv`.

Once complete, call `main.py` to run the application.


# Resources

1. [telethon documentation](https://docs.telethon.dev/en/stable/index.html)
