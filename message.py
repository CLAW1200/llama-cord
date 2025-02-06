# when the bot is mentioned, it will send a message to the channel it was mentioned in

import discord
from discord.ext import commands
from ollama import AsyncClient

class Message(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.ollama = AsyncClient()
        self.chat_history = []
        self.system_prompt = {
            'role': 'system',
            'content': 
            '''
            You are a poop doctor having a conversation with another poop doctor.
            You talk about poop and pee related topics.
            Keep your responses to 1 line.
            '''
        }

    def create_message(self, message: str, role: str):
        return {
            'role': role,
            'content': message
        }

    def wrap_message(self, message: str, user_id: str):
        return f"User id: {user_id}\nMessage: ```{message}```"

    async def chat(self, message: str):
        # add the user message to chat history first
        self.chat_history.append(self.create_message(role='user', message=message))
        
        # pop oldest messages if history exceeds 10 messages
        while len(self.chat_history) > 10:
            self.chat_history.pop(0)
        
        # call ollama API to get a response
        ollama_response = await self.ollama.chat(
            model='smollm:135m',
            messages=[self.system_prompt] + self.chat_history,  # include system prompt
            options={
                'temperature': 1.2,
                'num_predict': 350, # Maximum number of tokens to predict when generating text
                'top_k': 90,
                'top_p': 0.9,
                'repeat_penalty': 1.4,
            },
            stream=False
        )

        # create and add the assistant's response to chat history
        assistant_message = self.create_message(role='assistant', message=ollama_response['message']['content'])

        self.chat_history.append(assistant_message)
        # return the response content
        return assistant_message['content']

    def split_message(self, message: str, max_length: int = 1990) -> list[str]:
        """Split a message into chunks that respect Discord's character limit.
        
        Args:
            message (str): The message to split
            max_length (int, optional): Maximum length per chunk. Defaults to 1990.
            
        Returns:
            list[str]: List of message chunks
        """
        if len(message) <= max_length:
            return [message]
            
        chunks = []
        current_chunk = ""
        
        for word in message.split():
            if len(current_chunk) + len(word) + 1 <= max_length:
                current_chunk += " " + word if current_chunk else word
            else:
                chunks.append(current_chunk)
                current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk)
            
        return chunks

    def truncate_message(self, message: str, max_length: int = 1990) -> str:
        """Truncate a message to a maximum length.
        
        Args:
            message (str): The message to truncate
            max_length (int, optional): Maximum length of the truncated message. Defaults to 1990.

        Returns:
            str: The truncated message
        """
        if len(message) <= max_length:
            return message
        else:
            return message[:max_length] + "..."

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Only respond if:
        # 1. Message is not from a bot
        # 2. Bot is mentioned in the message or channel name is "bot-test"
        if (message.author != self.bot.user) and (self.bot.user in message.mentions or "yap" in message.channel.name):
            # if the bot's name contains "2"
            if "2" in self.bot.user.name and not message.author.bot:
                return
            async with message.channel.typing():
                content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()
                if not content:  # If message is empty after removing mention
                    await message.reply("[Input message is empty]")
                    return
                
                response = await self.chat(content)

                
                # Use the new split_message function
                message_to_send = self.truncate_message(response)
                await message.reply(message_to_send)


def setup(bot: commands.Bot):
    bot.add_cog(Message(bot))

