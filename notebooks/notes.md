# Notes

- `async with bot:` is a context manager similar to `with open`, just with the async syntax. For the telegram bot it appears to be the case that there is an inbuilt `await` included in the `async` with call, which basically means this portion will always execute immediately.

# Resources

1. Full Python [API reference documentation](https://docs.python-telegram-bot.org/en/v20.6/telegram.html)

2. Quick-start introduction to [building a bot in python](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Extensions---Your-first-Bot)

3. [High-level information on the API](https://core.telegram.org/bots/api)