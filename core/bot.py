from os import environ, getenv
from traceback import format_exception
import discord
from aiohttp import ClientSession
from discord.ext import commands
from .context import Context
import json
from pathlib import Path

class Bot(commands.Bot):
    def __init__(self) -> None:
        self.cache: dict[str, dict] = {"example_list": {}}
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        self.config_file = self.data_dir / "config.json"
        self.load_data()

        super().__init__(
            allowed_mentions=discord.AllowedMentions.none(),
            auto_sync_commands=False,
            chunk_guilds_at_startup=False,
            help_command=None,
            intents=discord.Intents(
                members=True,
                messages=True,
                message_content=True,
                guilds=True,
            ),
            owner_ids=set(self.db.get('bot', {}).get('owner_ids', [])),
        )

    def load_data(self) -> None:
        """Load data from config.json"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.db = json.load(f)
        else:
            self.db = {
                'bot': {
                    'presence': {
                        "presence_text": ""
                    },
                    'owner_ids': []
                }
            }
            self.save_data()

    def save_data(self) -> None:
        """Save data to config.json"""
        with open(self.config_file, 'w') as f:
            json.dump(self.db, f, indent=4)

    def get_emojis(self, emoji: str) -> discord.Emoji:
        return getenv(emoji)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        return await super().start(token, reconnect=reconnect)

    async def close(self) -> None:
        return await super().close()

    async def get_application_context(
        self, interaction: discord.Interaction
    ) -> Context:
        return Context(self, interaction)

    @property
    def http_session(self) -> ClientSession:
        return self.http._HTTPClient__session  # type: ignore # it exists

    async def on_ready(self) -> None:   
        self.errors_webhook = (
            discord.Webhook.from_url(
                webhook_url,
                session=self.http_session,
                bot_token=self.http.token,
            )
            if (webhook_url := getenv("ERRORS_WEBHOOK"))
            else None
        )
        # Get presence from JSON instead of database
        bot_data = self.db['bot']
        if bot_data and bot_data.get('presence'):
            activity = discord.CustomActivity(
                name=bot_data['presence']['presence_text']
            )
            await self.change_presence(activity=activity)
            print(f"Presence updated to watching {bot_data['presence']['presence_text']}")

        print(self.user, "is ready")

    async def on_application_command(self, ctx: discord.ApplicationContext):
        if ctx.guild is None:
            return await ctx.respond(
                "Commands are not supported in DMs. Please use commands in a server instead.",
                ephemeral=True
            )

    async def on_application_command_error(self, ctx: Context, error: Exception):
        if isinstance(error, discord.ApplicationCommandInvokeError):
            
            if isinstance((error := error.original), discord.HTTPException):
                message = (
                    "An HTTP exception has occurred: "
                    f"{error.status} {error.__class__.__name__}"
                )
                if error.text:
                    message += f": {error.text}"
                return await ctx.respond(message)
            
            if self.errors_webhook and not isinstance(error, discord.DiscordException):
                await ctx.respond(
                    "An unexpected error has occurred and the developer has been notified.\n"
                    "In the meantime, consider joining the support server.",
                    view=discord.ui.View(
                        discord.ui.Button(
                            label="Support", url="https://discord.gg/pApCNNVhy5"
                        ),
                        discord.ui.Button(
                            label="GitHub",
                            url="https://github.com/CLAW1200/Utility-Belt",
                        ),
                    ),
                )
                header = f"Command: `/{ctx.command.qualified_name}`"
                if ctx.guild is not None:
                    header += f" | Guild: `{ctx.guild.name} ({ctx.guild_id})`"
                
                options = []
                for option in ctx.interaction.data.get('options', []):
                    if isinstance(option, dict):
                        options.append(f"{option.get('name')}: {option.get('value')}")
                    elif isinstance(option, str):
                        options.append(option)
                options_str = " | ".join(options)

                with open("lastError.log", "w") as f:
                    f.write(f"{header}\nOptions: `{options_str}`\n{''.join(format_exception(type(error), error, error.__traceback__))}")
                
                return await self.errors_webhook.send(
                    f"{header}\nOptions: `{options_str}`\n",
                    file=discord.File("lastError.log"),
                )
            
        await ctx.edit(
            content="",
            embed=discord.Embed(
                title=error.__class__.__name__,
                description=str(f"{error}"),
                color=discord.Color.red(),
            ),
        )

    async def on_message_edit(
        self, before: discord.Message, after: discord.Message
    ) -> None:
        if before.content != after.content:
            await self.process_commands(after)

    async def on_guild_remove(self, guild: discord.Guild) -> None:
        pass
    
    def run(
        self, debug: bool = False, cogs: list[str] | None = None, sync: bool = False, test: bool = False
    ) -> None:
        token = getenv('TESTTOKEN' if test else 'TOKEN')
        self.load_extensions("jishaku", *cogs or ("cogs", "cogs.task"))
        if sync:
            async def on_connect() -> None:
                await self.sync_commands(delete_existing=not debug)
                print("Synchronized commands.")

            self.on_connect = on_connect

        environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")
        if debug:
            return super().run(token)

        environ.setdefault("JISHAKU_HIDE", "1")
        super().run(token)
