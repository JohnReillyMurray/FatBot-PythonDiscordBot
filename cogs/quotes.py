from discord.ext import commands
from .utils import checks
import json
import random
import re

FILE_NAME = 'quotes.json'
INPUT_REGEX = re.compile(r'"(.+)" \- ((\S+\s*)+)')
OUTPUT_FORMAT = '"{}" - {}'  # Quote - source
LIST_FORMAT = "\n{} - "
MAX_WHISPER_LENGTH = 1500

# Load all quotes

try:
    with open(FILE_NAME) as f:
        quotes = json.load(f)
except FileNotFoundError:
    print(f"Warning: {FILE_NAME} not found")
    quotes = []


def setup(bot):
    bot.add_cog(quotesCog(bot))


def save_quotes():
    with open(FILE_NAME, 'w') as f:
        json.dump(quotes, f, indent=4)


def format_quote(quote):
    return OUTPUT_FORMAT.format(quote[0], quote[1])


class quotesCog:
    """Commands for quotes"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def quote(self, *args):
        # If words were provided, use them to filter the quotes
        if args:
            # Filter for a word
            target = ' '.join(args)  # Combine the given words with spaces
            selection = [q for q in quotes if target.lower() in q.lower()]
        else:
            # Choose from all quotes
            selection = quotes
        # If there are any quotes, select from those, otherwise print a message
        if selection:
            quote = random.choice(selection)
            await self.bot.say(format_quote(quote))
        else:
            await self.bot.say("No quotes!")

    # *args would not give ' " ' character for some reason
    @commands.command(pass_context=True)
    async def savequote(self, ctx):
        args = ctx.message.content.split(' ')
        msg = ' '.join(args[1:])
        match = INPUT_REGEX.match(msg)
        if match:
            quotes.append((match.group(1), match.group(2)))  # List of (quote, source)
            save_quotes()
            await self.bot.say("Added quote: " + msg)
        else:
            await self.bot.say("Quotes must be of the form '\"Quote\" - Source'")

    @commands.command()
    @checks.admin_or_permissions(manage_roles=True)
    async def showquotes(self):
        quote_strs = [OUTPUT_FORMAT.format(*quote) for quote in quotes]
        msg = '\n'.join(quote_strs)
        msgs = []  # Used to split string into components so that each one is smaller than max size
        while len(msg) > MAX_WHISPER_LENGTH:
            try:
                pos = msg.rfind('\n', end=MAX_WHISPER_LENGTH)
            except ValueError:
                self.bot.whisper("Something went wrong. Maybe there's a quote that's too long?")
                return
            msgs.append(msg[:pos])
            msg = msg[pos:]
        for quote in quotes:
            msg += '\n' + OUTPUT_FORMAT.format(*quote)  # Unpack the quote for formatting
            if len(msg) >= MAX_WHISPER_LENGTH:
                await self.bot.whisper(msg)
                msg = "\n"
        await self.bot.whisper(msg)

    @commands.command(no_pm=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def removequote(self, index: int):
        """Removes the indexed quote from list of quotes

            Cannot be used in PMs"""
        if 0 <= index < len(quotes):
            to_remove = quotes[index]
            del quotes[index]
            save_quotes()
            await self.bot.say("Removed: " + to_remove)
        else:
            await self.bot.say("Invalid index")
