import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import os

# Replace YOUR_TOKEN_HERE with your Discord bot token
TOKEN = os.environ.get('DISCORD_TOKEN')
GUILD_ID = "603466164219281420"

# Define the intents you want to enable
intents = discord.Intents.default()
intents.members = True  # Enable the privileged members intent

# Create a new Discord bot client
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

    # Get the Discord guild object for the server you want to fetch threads from
    guild = bot.get_guild(GUILD_ID)

    # Get all the channels in the guild, including threads
    channels = await guild.fetch_channels()

    # Filter out only the threads from the channels list
    threads = [channel for channel in channels if isinstance(channel, discord.Thread)]

    # Print the name and ID of each thread
    for thread in threads:
        print(thread.name, thread.id)

# Run the bot using your Discord bot token
bot.run(TOKEN)
