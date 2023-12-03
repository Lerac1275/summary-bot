# Introduction

The goal of this project is to create a telegram bot that can summarize group chat messages on command. 

A user would be able to specify that they'd like a quick summary of messages from the last X hours, the bot would do its thing and return a short passage about the main topics being discussed. This was to be a simple solution to the problem of opening up a group chat and seeing 200 undread messages. 

# Workflow
The devised workflow would be as such:

1. Application (either a proper telegram account / telegram bot) is added to the group chat. 
2. A user tags the application and asks it to summarize the group chat messages from the last X hours. 
3. The application obtains all the group chat messages from that time period, and uses the openAI API to produce a short summary. 
4. That summary is sent to the group chat via the same application account. 

# Bot approach
Originally I thought this could be done using a conventional [telegram bot](https://core.telegram.org/bots/api). However telegram bots have a critical limitation: They cannot access historical chat messages in a chat group. 

The only way I can think of to make it work would be if the bot recorded each message in the group as they came in & stored them in some database. Then when the user request was made to summarize, it could access those stored messages. 

# Separate Account Apparoach
Fortunately there is an alternative. A conventional telegram user account has the permissions to access historical group chat messages. The API allows for programatic access to essentially all functionality that is available to a user via the app. 

The [telethon](https://docs.telethon.dev/en/stable/index.html) package in python provides an excellent way to interface with the Telegram API in python. 