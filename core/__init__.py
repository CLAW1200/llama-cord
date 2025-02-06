# "real men test in production"
from discord.ext import commands
from .bot import Bot
from .context import Context
from .utils import Lowercase, humanize_time, s, list_items

__all__ = (
    "Bot",
    "Cog",
    "Context",
    "Lowercase",
    "s",
    "list_items",
    "humanize_time",
)


class Cog(commands.Cog):
    """Base class for all cogs"""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
