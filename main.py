import os
import discord
from discord.ext import commands
from google import genai
from google.genai import types

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """
أنت مساعد ذكي مخصص لسيرفر ديسكورد يدير مهام ومشاريع وتفاعلات بين أعضاء يتحدثون الإنجليزية والعربية.
وظيفتك عند استلام رسالة أو صورة/سكرين شوت:
1. استخراج الفكرة أو النص الأساسي وترجمته إلى العربية والإنجليزية.
2. صياغة رد أو تعليق احترافي ومناسب جداً لسياق المشروع، المنشور، أو المحادثة.
3. كتابة الرد باللغتين (الإنجليزية مع ترجمتها للعربية).
اجعل التنسيق واضحاً ومرتباً بنقاط تناسب ديسكورد.
"""

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح كـ: {bot.user.name}")

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if not welcome_channel:
        welcome_channel = member.guild.system_channel
    
    if welcome_channel:
        embed = discord.Embed(
            title="👋 مرحباً بك / Welcome!",
            description=(
                f"أهلاً بك {member.mention} في سيرفر المشاريع والمهام!\n"
                f"Welcome to the Projects & Tasks Server! Feel free to collaborate and interact."
            ),
            color=discord.Color.blue()
        )
        await welcome_channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    has_text = bool(message.content.strip())
    has_image = any(att.content_type and att.content_type.startswith("image/") for att in message.attachments)

    if not has_text and not has_image:
        return

    async with message.channel.typing():
        try:
            contents = []

            for att in message.attachments:
                if att.content_type and att.content_type.startswith("image/"):
                    img_bytes = await att.read()
                    contents.append(
                        types.Part.from_bytes(
                            data=img_bytes,
                            mime_type=att.content_type
                        )
                    )

            prompt_text = message.content.strip() if has_text else "حلل هذه الصورة/السكرين شوت، ترجم محتواها، واقترح تعليقاً وردّاً مناسباً للمشروع."
            contents.append(prompt_text)

            response = ai_client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.7
                )
            )

            reply_text = response.text
            if len(reply_text) <= 2000:
                await message.reply(reply_text)
            else:
                for chunk in [reply_text[i:i+1900] for i in range(0, len(reply_text), 1900)]:
                    await message.reply(chunk)

        except Exception as e:
            print(f"حدث خطأ أثناء المعالجة: {e}")

bot.run(os.getenv("DISCORD_TOKEN"))
