import discord
from core import Cog
from ollama import AsyncClient
from dataclasses import dataclass
import random
import aiohttp
from typing import Optional, List, Dict
from core.utils import cleanup_webhooks, get_or_create_webhook
import time

@dataclass
class AgentTemplate:
    """Class to represent an agent template"""
    agent_name: str
    personality: str
    avatar_url: str
    active: bool = True  # Add active status with default True

default_agent_templates = [
            AgentTemplate(
                agent_name="politics",
                personality="You are a political agent. Focus on discussing political events and world affairs.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="sports",
                personality="You are a sports agent. Focus on sports news and athletic achievements.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="finance", 
                personality="You are a finance agent. Focus on financial markets and economic news.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="tech",
                personality="You are a tech agent. Focus on technology trends and innovations.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="entertainment",
                personality="You are a entertainment agent. Focus on movies, music, and pop culture.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            ),
            AgentTemplate(
                agent_name="science",
                personality="You are a science agent. Focus on scientific discoveries and research.",
                avatar_url="https://thispersondoesnotexist.com/",
                active=True
            )
        ]

@dataclass
class Agent:
    """Class to represent an AI agent"""
    name: str
    system_prompt: str
    webhook: Optional[discord.Webhook] = None
    history: List[Dict] = None

    def __post_init__(self):
        if self.history is None:
            self.history = []


class AgentCog(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.client = AsyncClient()
        self.agents = {}
        self.active_webhooks = {}  # Add this to track active webhooks
        self.global_model = "llama3.2"
        self.global_system_prompt = """You are participating in a multi-agent conversation. Keep your responses short and relevant.
        Always stay in character and respond from your specialized perspective while engaging meaningfully with other agents' messages."""
        self.agent_templates = default_agent_templates
        self.global_temperature = 0.8
        self.global_num_ctx = 2048
        self.global_top_k = 40
        self.global_top_p = 0.9
        self.global_repeat_penalty = 1.1
        self.global_num_predict = 150


    async def cleanup_webhooks(self, channel):
        """Clean up existing webhooks created by the bot"""
        await cleanup_webhooks(channel, self.bot.user)

    async def get_or_create_webhook(self, channel, name, avatar_data=None):
        """Get existing webhook or create a new one"""
        return await get_or_create_webhook(channel, name, self.bot.user, avatar_data)

    async def create_agent_webhooks(self, channel, agent_names):
        """Create webhooks for the agents"""
        async with aiohttp.ClientSession() as session:
            for name in agent_names:
                # Extract the agent_name from agent name (e.g., "agent_politics" -> "politics")
                agent_name = name.split('_')[1]
                template = next((t for t in self.agent_templates if t.agent_name == agent_name), None)
                
                avatar_data = None
                if template and template.avatar_url:
                    async with session.get(template.avatar_url) as response:
                        if response.status == 200:
                            avatar_data = await response.read()
                
                webhook = await self.get_or_create_webhook(
                    channel=channel,
                    name=name.capitalize(),
                    avatar_data=avatar_data
                )
                self.agents[name.lower()].webhook = webhook

    def create_agents(self, num_agents):
        """Create the specified number of agents"""
        # check agent templates
        active_templates = [t for t in self.agent_templates if t.active]
        if len(active_templates) == 0:
            raise discord.errors.ApplicationCommandError("No active agent templates found")
        
        # Check if we have enough templates
        if num_agents > len(active_templates):
            raise discord.errors.ApplicationCommandError(
                f"Not enough active agent templates. Requested {num_agents} agents but only have {len(active_templates)} active templates. "
                "Please activate more agent templates or request fewer agents."
            )

        # Clear existing agents
        self.agents = {}
        
        # Create the requested number of agents from active templates only
        for i in range(num_agents):
            template = active_templates[i % len(active_templates)]
            agent_name = f"agent_{template.agent_name}"
            
            self.agents[agent_name] = Agent(
                name=agent_name.capitalize(),
                system_prompt=f"{self.global_system_prompt}\n\n{template.personality}"
            )

    def update_chat_history(self, agent_name, role, content):
        """Update an agent's chat history, maintaining max 10 messages"""
        agent = self.agents[agent_name]
        agent.history.append({"role": role, "content": content})
        agent.history = agent.history[-10:] if len(agent.history) > 10 else agent.history

    async def get_ai_response(self, agent_name, message):
        """Get response from Ollama for the specified agent"""
        start_time = time.time()
        
        agent = self.agents[agent_name]
        
        # Update history with the received message
        self.update_chat_history(agent_name, "user", message)
        
        # Construct messages list with system prompt and chat history
        messages = [
            {
                "role": "system",
                "content": f"{agent.system_prompt}\nThe current topic being discussed is: {message}"
            }
        ] + agent.history
        
        response = await self.client.chat(
            model=self.global_model,
            messages=messages,
            options={
                'temperature': self.global_temperature,
                'num_predict': self.global_num_predict,
                'repeat_penalty': self.global_repeat_penalty,
                'top_k': self.global_top_k,
                'top_p': self.global_top_p,
                'num_ctx': self.global_num_ctx,
            },
            stream=False
        )
        
        generation_time = time.time() - start_time
        
        # Update history with the AI's response
        self.update_chat_history(agent_name, "assistant", response.message.content)
        return response.message.content, generation_time

    async def send_chunked_message(self, webhook, content):
        """Send a message in chunks if it exceeds Discord's character limit"""
        MAX_LENGTH = 2000
        
        if len(content) <= MAX_LENGTH:
            await webhook.send(content=content)
            return
            
        chunks = []
        while content:
            if len(content) <= MAX_LENGTH:
                chunks.append(content)
                break
                
            # Find the last space within the limit
            split_index = content.rfind(' ', 0, MAX_LENGTH)
            if split_index == -1:  # No space found, force split
                split_index = MAX_LENGTH
                
            chunks.append(content[:split_index])
            content = content[split_index:].strip()
            
        for chunk in chunks:
            await webhook.send(content=chunk)

    async def start_conversation(self, channel, initial_topic="Tell me about yourself", turns: int = 3, random_order: bool = False):
        """Start a conversation between agents"""
        agent_names = list(self.agents.keys())
        if not agent_names:
            raise discord.errors.ApplicationCommandError("No agents created")

        # Create or update webhooks
        await self.create_agent_webhooks(channel, agent_names)
        
        # Reset chat histories
        for agent in self.agents.values():
            agent.history = []
            
        # Initial message from first agent
        current_message = initial_topic
        first_agent = random.choice(agent_names) if random_order else agent_names[0]
        response, gen_time = await self.get_ai_response(first_agent, current_message)
        await self.send_chunked_message(self.agents[first_agent].webhook, response)
        current_message = response
        
        total_time = gen_time
        message_count = 1
        
        # Keep track of the last speaker to avoid repetition
        last_speaker = first_agent
        
        # Start conversation loop
        for _ in range(turns):
            available_agents = [name for name in agent_names if name != last_speaker]
            
            if random_order:
                random.shuffle(available_agents)
                
            for agent_name in available_agents:
                response, gen_time = await self.get_ai_response(agent_name, current_message)
                await self.send_chunked_message(self.agents[agent_name].webhook, response)
                current_message = response
                last_speaker = agent_name
                total_time += gen_time
                message_count += 1
                
        return total_time, message_count

    # Create agent command group
    agent = discord.SlashCommandGroup("agent", "Commands for managing and interacting with AI agents")

    @agent.command(name="simulation", description="Start a conversation between agents")
    @discord.option(name="agents", description="The number of agents to start", required=False, default=2)
    @discord.option(name="topic", description="The topic of the conversation", required=False)
    @discord.option(name="turns", description="The number of turns in the conversation", required=False, default=3)
    @discord.option(name="random_order", description="Whether to shuffle the order of the agents", required=False, default=False)
    @discord.option(name="channel", description="The channel to send messages to", type=discord.TextChannel, required=False)
    async def agent_simulation(self, ctx, num_agents: int = 2, topic: str = None, turns: int = 3, random_order: bool = False, channel: discord.TextChannel = None):
        """Command to start a conversation between agents"""
        await ctx.defer()
        
        # Use provided channel or default to command channel
        target_channel = channel or ctx.channel
        
        order_type = "random" if random_order else "sequential"
        progress_msg = await ctx.respond(
            f"🤖 Starting conversation with {num_agents} agents in {order_type} order...\n"
            f"Output channel: {target_channel.mention}"
        )

        await progress_msg.edit(content="🎭 Creating agents...")
        self.create_agents(num_agents)

        await progress_msg.edit(content="💬 Generating responses...")
        total_time, message_count = await self.start_conversation(target_channel, topic, turns, random_order)
        
        avg_time = total_time / message_count
        await progress_msg.edit(
            content=f"✨ Conversation completed in {target_channel.mention}!\n"
            f"Total time: {total_time:.2f}s\n"
            f"Messages: {message_count}\n"
            f"Average generation time: {avg_time:.2f}s per message"
        )

    @agent.command(name="create", description="Create a new agent with a specific personality")
    @discord.option(name="agent_name", description="The name of the agent", required=True)
    @discord.option(name="personality", description="The personality of the agent", required=True)
    @discord.option(name="avatar_url", description="The avatar of the agent", required=False)
    async def agent_create(self, ctx, agent_name: str, personality: str, avatar_url: str = None):
        """Command to create a new agent with a specific personality"""
        if not avatar_url:
            avatar_url = "https://thispersondoesnotexist.com/"
            
        # Check if agent already exists
        if any(t.agent_name == agent_name for t in self.agent_templates):
            embed = discord.Embed(
                title="❌ Agent Already Exists",
                description=f"An agent with name '{agent_name}' already exists",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            return
            
        self.agent_templates.append(AgentTemplate(
            agent_name=agent_name,
            personality=personality, 
            avatar_url=avatar_url,
            active=True
        ))
        
        embed = discord.Embed(
            title="✅ Agent Created",
            description=f"Successfully created agent: **{agent_name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Personality", value=personality, inline=False)
        embed.add_field(name="Status", value="Active 🟢", inline=True)
        
        await ctx.respond(embed=embed)

    @agent.command(name="delete", description="Delete an agent")
    @discord.option(name="agent_name", description="The name of the agent", required=True)
    async def agent_delete(self, ctx, agent_name: str):
        """Command to delete an agent"""
        await ctx.defer()
        agent_name = agent_name.lower()
        # Check if agent exists before deletion
        agent = next((t for t in self.agent_templates if t.agent_name == agent_name), None)
        if not agent:
            embed = discord.Embed(
                title="❌ Agent Not Found",
                description=f"No agent found with name '{agent_name}'",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
            return

        self.agent_templates = [t for t in self.agent_templates if t.agent_name != agent_name]
        
        embed = discord.Embed(
            title="🗑️ Agent Deleted",
            description=f"Successfully deleted agent: **{agent_name}**",
            color=discord.Color.green()
        )
        embed.add_field(name="Personality", value=agent.personality, inline=False)
        
        await ctx.respond(embed=embed)

    @agent.command(name="delete_all", description="Delete all agents")
    async def agent_delete_all(self, ctx):
        """Command to delete all agents"""
        agent_count = len(self.agent_templates)
        self.agent_templates = []
        
        embed = discord.Embed(
            title="🗑️ All Agents Deleted",
            description=f"Successfully deleted {agent_count} agents",
            color=discord.Color.green()
        )
        await ctx.respond(embed=embed)

    @agent.command(name="list", description="List all agents")
    async def agent_list(self, ctx):
        """Command to list all agents in an embed format"""
        embed = discord.Embed(
            title="Available Agents",
            description="Here are all the agent templates:",
            color=discord.Color.blue()
        )
        
        if not self.agent_templates:
            embed.add_field(
                name="No Agents Found",
                value="There are currently no agent templates. Use `/create_agent` to create one or `/default_agents` to load the defaults.",
                inline=False
            )
        else:
            for template in self.agent_templates:
                status = "Active 🟢" if template.active else "Inactive 🔴"
                embed.add_field(
                    name=f"🤖 {template.agent_name.title()} [ {status} ]",
                    value=f"**Personality:** {template.personality}",
                    inline=False
                )

        await ctx.respond(embed=embed)
    
    @agent.command(name="default", description="Create the default agents")
    async def agent_default(self, ctx):
        """Command to create the default agents"""
        await ctx.defer()
        previous_count = len(self.agent_templates)
        self.agent_templates = default_agent_templates
        
        embed = discord.Embed(
            title="✅ Default Agents Created",
            description="Successfully loaded default agent templates",
            color=discord.Color.green()
        )
        embed.add_field(
            name="Agents Loaded", 
            value=f"Previous agents: {previous_count}\nNew agents: {len(self.agent_templates)}",
            inline=False
        )
        embed.add_field(
            name="Available Agents",
            value="\n".join([f"• {t.agent_name}" for t in self.agent_templates]),
            inline=False
        )
        
        await ctx.respond(embed=embed)

    async def setup_temporary_agent(self, agent_name: str, channel) -> tuple[str, Agent, discord.Webhook]:
        """Create a temporary agent and webhook for one-time use"""
        template = next((t for t in self.agent_templates if t.agent_name.lower() == agent_name.lower()), None)
        if not template:
            raise ValueError(f"Agent '{agent_name}' not found. Available agents: {', '.join([t.agent_name for t in self.agent_templates])}")

        agent_name = f"agent_{template.agent_name}"
        temp_agent = Agent(
            name=agent_name.capitalize(),
            system_prompt=f"{self.global_system_prompt}\n\n{template.personality}"
        )
        
        # Create or get webhook using existing session
        async with aiohttp.ClientSession() as session:
            avatar_data = None
            if template.avatar_url:
                async with session.get(template.avatar_url) as response:
                    if response.status == 200:
                        avatar_data = await response.read()
            
            webhook = await self.get_or_create_webhook(
                channel=channel,
                name=agent_name.capitalize(),
                avatar_data=avatar_data
            )
            
        return agent_name, temp_agent, webhook

    @agent.command(name="ask", description="Ask a question to an agent")
    @discord.option(name="agent", description="The agent to ask", required=True)
    @discord.option(name="question", description="The question to ask", required=True)
    async def agent_ask(self, ctx, agent: str, question: str):
        await ctx.defer()
        progress_msg = await ctx.respond("🎭 Setting up agent...")
        
        try:
            await progress_msg.edit(content="🌐 Creating webhook...")
            # Setup temporary agent
            agent_name, temp_agent, webhook = await self.setup_temporary_agent(agent, ctx.channel)
            
            # Store agent and webhook
            self.agents[agent_name] = temp_agent
            self.agents[agent_name].webhook = webhook
            self.active_webhooks[str(webhook.id)] = webhook
            
            await progress_msg.edit(content="💬 Generating response...")
            # Get and send response
            response, gen_time = await self.get_ai_response(agent_name, question)
            await self.send_chunked_message(webhook, response)
            
        except ValueError as e:
            raise discord.errors.ApplicationCommandError(str(e))
        except Exception as e:
            raise discord.errors.ApplicationCommandError(str(e))
        finally:
            # Only cleanup the temporary agent, keep the webhook
            if agent_name in self.agents:
                del self.agents[agent_name]
        
        await progress_msg.edit(content=f"✨ Response sent! (Generated in {gen_time:.2f}s)")

    @agent.command(name="toggle", description="Toggle an agent's active status")
    @discord.option(name="agent_name", description="The name of the agent to toggle", required=True)
    async def agent_toggle(self, ctx, agent_name: str):
        """Command to toggle an agent's active status"""
        template = next((t for t in self.agent_templates if t.agent_name.lower() == agent_name.lower()), None)
        if template:
            template.active = not template.active
            status = "activated" if template.active else "deactivated"
            await ctx.respond(f"Agent '{agent_name}' has been {status}")
        else:
            await ctx.respond(f"Agent '{agent_name}' not found", ephemeral=True)

    @discord.Cog.listener()
    async def on_message(self, message):
        """Handle replies to webhook messages"""
        if message.author.bot:
            return
            
        # Check if this is a reply to a message
        if not message.reference:
            return
            
        try:
            # Get the original message that was replied to
            original_message = await message.channel.fetch_message(message.reference.message_id)
            
            # Check if the original message was from one of our webhooks
            if not original_message.webhook_id:
                return

            webhook_id = str(original_message.webhook_id)
            webhook_name = original_message.author.name

            # First try to find existing webhook in the guild
            existing_webhook = None
            guild_webhooks = await message.channel.guild.webhooks()
            for webhook in guild_webhooks:
                if (webhook.user and webhook.user.id == self.bot.user.id and 
                    webhook.name.lower() == webhook_name.lower()):
                    existing_webhook = webhook
                    # Update channel if needed
                    if webhook.channel_id != message.channel.id:
                        existing_webhook = await webhook.edit(channel=message.channel)
                    break

            # Create new webhook only if none exists
            webhook = existing_webhook or await message.channel.create_webhook(name=webhook_name)
            self.active_webhooks[webhook_id] = webhook

            agent_name = webhook.name.lower()
            
            # Construct context with the original message and user's reply
            context = f"Previous message: {original_message.content}\nUser's reply: {message.content}"
            
            # Setup temporary agent for response
            temp_agent_name, temp_agent, temp_webhook = await self.setup_temporary_agent(
                agent_name.split('_')[1] if '_' in agent_name else agent_name, 
                message.channel
            )
            
            # Store agent temporarily
            self.agents[temp_agent_name] = temp_agent
            self.agents[temp_agent_name].webhook = temp_webhook
            
            try:
                # Get and send response using the combined context
                response, gen_time = await self.get_ai_response(temp_agent_name, context)
                await webhook.send(content=response)  # Use existing webhook instead of temp_webhook
            finally:
                # Only cleanup the temporary agent, keep the webhook
                if temp_agent_name in self.agents:
                    del self.agents[temp_agent_name]
                
        except Exception as e:
            print(f"Error handling webhook reply: {e}")
            return

    async def cleanup_inactive_webhooks(self):
        """Cleanup webhooks that haven't been used in a while"""
        for webhook_id, webhook in list(self.active_webhooks.items()):
            try:
                await webhook.delete()
            except:
                pass
            del self.active_webhooks[webhook_id]

def setup(bot):
    bot.add_cog(AgentCog(bot))


