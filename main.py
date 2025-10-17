import discord
from discord.ext import commands
import os
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = "n", intents=intents)

class BotData:
    def __init__(self):
        self.welcome_channel = None
        self.goodbye_channel = None

        self.reaction_role = None
        self.reaction_message = None

botdata = BotData()
@bot.event
async def on_ready():
    print("Your bot is ready.")


@bot.command()
async def dm_all(ctx, *, args=None):
    if args != None:
        members = ctx.guild.members
        for member in members:
            try:
                await member.send(args)
                print("'" + args + "' sent to: " + member.name)

            except:
                print("Couldn't send '" + args + "' to: " + member.name)

    else:
        await ctx.channel.send("A message was not provided.")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int | None = None):
    if limit is None:
        # Delete messages from the last 1 minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        deleted = await ctx.channel.purge(after=one_minute_ago, limit=None)
        await ctx.send(f"Deleted {len(deleted)} message(s) from the last 1 minute.", delete_after=5)
        print(f"Purged {len(deleted)} messages from the last 1 minute in #{ctx.channel.name}")
    else:
        # Delete specified number of messages
        deleted = await ctx.channel.purge(limit=limit + 1)  # +1 to include the command message
        await ctx.send(f"Deleted {len(deleted) - 1} message(s).", delete_after=5)
        print(f"Purged {len(deleted) - 1} messages in #{ctx.channel.name}")


@bot.command()
async def invite(ctx):
    if bot.user is None:
        await ctx.send("Bot is not ready yet. Please try again in a moment.")
        return
        
    permissions = discord.Permissions(
        manage_messages=True,
        send_messages=True,
        read_messages=True,
        manage_roles=True,
        kick_members=True,
        ban_members=True
    )
    invite_url = discord.utils.oauth_url(bot.user.id, permissions=permissions)
    
    embed = discord.Embed(
        title="Invite Me!",
        description=f"Click [here]({invite_url}) to invite me to your server!",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}")
    
    await ctx.send(embed=embed)
    print(f"Invite link requested by {ctx.author.name} in #{ctx.channel.name}")


@bot.command()
async def ticket(ctx):
    guild = ctx.guild
    user = ctx.author
    
    # Create ticket category if it doesn't exist
    category = discord.utils.get(guild.categories, name="Tickets")
    if not category:
        category = await guild.create_category("Tickets")
    
    # Check if user already has a ticket
    existing_ticket = discord.utils.get(guild.text_channels, name=f"ticket-{user.name.lower()}")
    if existing_ticket:
        await ctx.send(f"You already have an open ticket: {existing_ticket.mention}", delete_after=10)
        return
    
    # Create ticket channel
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
    }
    
    # Add permission for roles with manage_messages (staff/admins)
    for role in guild.roles:
        if role.permissions.manage_messages:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
    
    ticket_channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        category=category,
        overwrites=overwrites
    )
    
    # Send welcome message in ticket
    embed = discord.Embed(
        title="Support Ticket",
        description=f"{user.mention}, welcome to your support ticket!\nA staff member will be with you shortly.\n\nTo close this ticket, use `nclose`",
        color=discord.Color.green()
    )
    await ticket_channel.send(embed=embed)
    
    # Confirm ticket creation
    await ctx.send(f"Ticket created: {ticket_channel.mention}", delete_after=10)
    print(f"Ticket created for {user.name}")


@bot.command()
async def close(ctx):
    if not ctx.channel.name.startswith("ticket-"):
        await ctx.send("This command can only be used in ticket channels.", delete_after=5)
        return
    
    embed = discord.Embed(
        title="Closing Ticket",
        description="This ticket will be closed in 5 seconds...",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    
    await discord.utils.sleep_until(discord.utils.utcnow() + timedelta(seconds=5))
    await ctx.channel.delete()
    print(f"Ticket {ctx.channel.name} closed by {ctx.author.name}")


token = os.environ.get("DISCORD_BOT_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_BOT_TOKEN not found in environment variables")