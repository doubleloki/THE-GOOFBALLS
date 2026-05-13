import discord
from discord.ext import commands
import os
import random

# --- BOT CONFIG ---
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user.name} is online and ready to build!')

# --- 1. THE BIG SERVER BUILDER ---
@bot.command()
@commands.has_permissions(administrator=True)
async def build_server(ctx):
    guild = ctx.guild
    print(f"Starting professional build for {guild.name}...")

    # Create Roles
    role_data = {
        "OWNER": 0x9b59b6, 
        "ADMIN": 0xe74c3c, 
        "DEV": 0x3498db, 
        "STREAMER": 0xf1c40f, 
        "MEMBER": 0x2ecc71
    }
    
    created_roles = {}
    for name, color_hex in role_data.items():
        role = await guild.create_role(name=name, color=discord.Color(color_hex), hoist=True)
        created_roles[name] = role

    await ctx.author.add_roles(created_roles["OWNER"])

    # Build Categories & Channels
    # Info
    info_cat = await guild.create_category("━━━ INFORMATION ━━━")
    await guild.create_text_channel("rules", category=info_cat)
    await guild.create_text_channel("roles-selection", category=info_cat)
    await guild.create_text_channel("vc-pings", category=info_cat)

    # Chat Hub
    chat_cat = await guild.create_category("━━━ CHAT HUB ━━━")
    await guild.create_text_channel("just-chatting", category=chat_cat)
    await guild.create_text_channel("food-pics", category=chat_cat)
    await guild.create_text_channel("selfies", category=chat_cat)

    # Voice Lounges (1-10)
    vc_cat = await guild.create_category("━━━ VOICE LOUNGES ━━━")
    for i in range(1, 11):
        await guild.create_voice_channel(f"VC-{i}", category=vc_cat)

    # Specialty VCs
    spec_cat = await guild.create_category("━━━ SPECIALTY ━━━")
    await guild.create_stage_channel(name="Event Stage", category=spec_cat)
    await guild.create_voice_channel("Sleep Call (Private)", category=spec_cat, user_limit=2)

    # Staff Zone
    staff_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        created_roles["ADMIN"]: discord.PermissionOverwrite(read_messages=True),
        created_roles["OWNER"]: discord.PermissionOverwrite(read_messages=True)
    }
    staff_cat = await guild.create_category("━━━ STAFF ONLY ━━━", overwrites=staff_overwrites)
    await guild.create_text_channel("admin-chat", category=staff_cat)
    await guild.create_voice_channel("Admin VC", category=staff_cat)

    await ctx.send("🚀 **Server Construction Complete!** All channels, roles, and permissions are set.")

# --- 2. ADMIN TOOLS ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    """Deletes messages: !clear 10"""
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ Deleted {amount} messages.", delete_after=3)

# --- 3. VC UTILITIES ---
@bot.command()
async def vcping(ctx):
    """Pings the Member role for VC action"""
    role = discord.utils.get(ctx.guild.roles, name="MEMBER")
    mention = role.mention if role else "@everyone"
    await ctx.send(f"🎙️ {ctx.author.mention} wants to start a VC! {mention}")

# --- 4. AUTO-WELCOME ---
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="just-chatting")
    if channel:
        embed = discord.Embed(
            title=f"Welcome {member.name}!", 
            description="We're a VC-focused server. Grab some roles in <#roles-selection>!",
            color=discord.Color.blue()
        )
        await channel.send(content=member.mention, embed=embed)
    
    role = discord.utils.get(member.guild.roles, name="MEMBER")
    if role:
        await member.add_roles(role)

bot.run(TOKEN)
