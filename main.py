import os
import discord
from discord.ext import commands
import google.generativeai as genai

DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ البوت متصل وشغال 24/7 سحابياً باسم: {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    async with message.channel.typing():
        try:
            prompt = (
                "أنت مساعد مترجم ومقترح ردود داخل سيرفر ديسكورد.\n"
                "إذا كانت الرسالة بالإنجليزية: ترجمها للعربية باحترافية واقترح رداً بالإنجليزية.\n"
                "إذا كانت بالعربية: ترجمها للإنجليزية واقترح رداً بالعربية.\n\n"
                f"نص الرسالة:\n{message.content}"
            )
            response = model.generate_content(prompt)
            await message.reply(response.text.strip())
        except Exception as e:
            print(f"Error: {e}")

bot.run(DISCORD_TOKEN)
