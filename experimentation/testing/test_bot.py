# Introductory notes taken from: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot

import logging
from telegram import Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler
# Inline query packages
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler

from dotenv import load_dotenv
import os
load_dotenv()
# Load Bot Token
bot_token=os.environ.get("KevinMaloneBot_Token")

# For logging purposes
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

####################
# Command Handlers #
####################
# Functions to handle specific commands (invoked in the chat by /<command>). Each function takes in the telegram update (message / user / etc), and the context (e.g. the Bot iteslf)

# Handle the /start command. Will return a greeting message.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

# Handle the /echo command. Will list all messages from that chat. 
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# Handle unknown commands
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

# Returns the argument following the invoking of this command in all caps
async def caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Note that arguments in a messsage following a command are received as a list split on spaces
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

# Same as above but for inline functionality (aka you can call this bot from anywhere and it will return the message following the call in all caps)
async def inline_caps(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query
    if not query:
        return
    results = []
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    await context.bot.answer_inline_query(update.inline_query.id, results)

if __name__ == '__main__':
    # Instantiate an application class with the bot token.
    application = ApplicationBuilder().token(bot_token).build()
    # Instantiate the /start command handler with the function defined above. It will handle the 'start' command
    start_handler = CommandHandler('start', start)
    # Instantiate handler to handle /caps
    caps_handler = CommandHandler('caps', caps)
    # Message handler to handle unknown commands
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    # Instantiate a MessageHandler. This will respond to all messages THAT ARE NOT COMMANDS
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    # Instantiate an inline query handler
    inline_caps_handler = InlineQueryHandler(inline_caps)
    # Add the inline query handler to the application
    application.add_handler(inline_caps_handler)
    # Add the defined command handler to the application
    application.add_handler(start_handler)
    application.add_handler(caps_handler)
    # Add the defined message handler to the application
    application.add_handler(echo_handler)
    # NOTE THAT THE UNKOWN COMMAND HANDLER MUST BE ADDED LAST. Otherwise it would be triggered before the other command handlers
    application.add_handler(unknown_handler)
    # Runs the bot until the application is exited / shut down
    application.run_polling()