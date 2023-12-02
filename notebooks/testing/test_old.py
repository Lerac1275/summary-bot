import asyncio
import telegram

from dotenv import load_dotenv
import os
load_dotenv()
# Load Bot Token
bot_token=os.environ.get("KevinMaloneBot_Token")

async def check_bot(token):
    """
    Checks the validity of a given bot token
    """
    bot = telegram.Bot(token)
    async with bot:
        bot_info = await bot.get_me()
        print(123)
    print(234)

# async def main():
#     bot = telegram.Bot(bot_token)
#     async with bot:
#         print(await bot.get_me())

async def main():
    bot = telegram.Bot(bot_token)
    


    async with bot:
        print((await bot.get_updates())[0])

if __name__ == main:
    asyncio.run(main())