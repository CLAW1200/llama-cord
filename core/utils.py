from discord import DiscordException
from discord.ext import commands
from typing import Any, Literal
import datetime
from datetime import timedelta
import discord
from typing import Optional

__all__ = (
    "s",
    "list_items",
    "humanize_time",
    "Lowercase",
    "BotMissingPermissions",
)

# functions
def s(data) -> Literal["", "s"]:
    if isinstance(data, str):# if data is a string
        data = int(not data.endswith("s")) # if the string ends with s, return 0, else return 1
    elif hasattr(data, "__len__"): # if data has a length 
        data = len(data) # get the length of the data
    check = data != 1 # if data is not equal to 1
    return "s" if check else "" # return s if check is true, else return an empty string


def list_items(items) -> str:
    return (
        f"{', '.join(items[:-1])} and {items[-1]}"
        if len(items) > 1
        else items[0]
    )

def humanize_time(time: timedelta) -> str:
    if time.days > 365:
        years, days = divmod(time.days, 365)
        return f"{years} year{s(years)} and {days} day{s(days)}"
    if time.days > 1:
        return f"{time.days} day{s(time.days)}, {humanize_time(timedelta(seconds=time.seconds))}"
    hours, seconds = divmod(time.seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if hours > 0:
        return f"{hours} hour{s(hours)} and {minutes} minute{s(minutes)}"
    if minutes > 0:
        return f"{minutes} minute{s(minutes)} and {seconds} second{s(seconds)}"
    return f"{seconds} second{s(seconds)}"

# converters
class _Lowercase(commands.Converter):
    async def convert(self, ctx, text):
        return text.lower()

Lowercase: Any = _Lowercase()

# exceptions
class BotMissingPermissions(DiscordException):
    def __init__(self, permissions) -> None:
        missing = [
            f"**{perm.replace('_', ' ').replace('guild', 'server').title()}**"
            for perm in permissions
        ]
        sub = (
            f"{', '.join(missing[:-1])} and {missing[-1]}"
            if len(missing) > 1
            else missing[0]
        )
        super().__init__(f"I require {sub} permissions to run this command.")


async def cleanup_webhooks(channel: discord.TextChannel, bot_user: discord.User):
    """Clean up existing webhooks created by the bot"""
    webhooks = await channel.webhooks()
    for webhook in webhooks:
        if webhook.user == bot_user:
            await webhook.delete()

async def get_or_create_webhook(channel: discord.TextChannel, name: str, bot_user: discord.User, avatar_data: Optional[bytes] = None):
    """Get existing webhook or create a new one"""
    # First check all webhooks in the guild
    guild_webhooks = await channel.guild.webhooks()
    
    # Look for existing webhook with same name created by the bot
    existing_webhook = next(
        (w for w in guild_webhooks 
         if w.name.lower() == name.lower() 
         and w.user and w.user.id == bot_user.id),
        None
    )
    
    if existing_webhook:
        # If webhook exists but in wrong channel, modify it
        if existing_webhook.channel_id != channel.id:
            await existing_webhook.edit(channel=channel)
        return existing_webhook
        
    # Create new webhook if none exists
    return await channel.create_webhook(
        name=name,
        avatar=avatar_data
    ) 