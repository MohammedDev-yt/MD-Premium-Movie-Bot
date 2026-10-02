# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import os
import time
import asyncio
import platform
import psutil

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram import filters
from pyrogram.enums import ParseMode

BOT_START_TIME = time.time()

SYSTEM_IMAGE = os.getenv(
    "SYSTEM_IMAGE",
    "https://graph.org/file/186013fea801dbb851bbd-8df16c2f5040ac02c7.jpg"
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================
# SMALL CAPS
# ============================

SMALL_CAPS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def smallcaps(text):
    return text.translate(SMALL_CAPS)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def format_uptime(seconds):

    seconds = int(seconds)

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return (
        f"{hours}ʜ : "
        f"{minutes}ᴍ : "
        f"{secs}s"
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_system_text():

    bot_uptime = time.time() - BOT_START_TIME

    system_uptime = (
        time.time() - psutil.boot_time()
    )

    memory = psutil.virtual_memory()

    ram_used = memory.used / (
        1024 * 1024
    )

    ram_total = memory.total / (
        1024 * 1024
    )

    disk = psutil.disk_usage("/")

    disk_used = disk.used / (
        1024 * 1024 * 1024
    )

    disk_total = disk.total / (
        1024 * 1024 * 1024
    )

    os_name = platform.system()

    return (
        f"<b>{smallcaps('💻 System Information')}</b>\n\n"

        f"🖥️ <b>{smallcaps('OS')}:</b> "
        f"{os_name}\n"

        f"⏰ <b>{smallcaps('Bot Uptime')}:</b> "
        f"{format_uptime(bot_uptime)}\n"

        f"🔄 <b>{smallcaps('System Uptime')}:</b> "
        f"{format_uptime(system_uptime)}\n"

        f"💾 <b>{smallcaps('RAM Usage')}:</b> "
        f"{ram_used:.2f} MB / "
        f"{ram_total:.2f} MB\n"

        f"📁 <b>{smallcaps('Disk Usage')}:</b> "
        f"{disk_used:.2f} GB / "
        f"{disk_total:.2f} GB\n\n"

        f"<b>{smallcaps('Powered By')} @Aero_Unity</b>"
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def register_system_handlers(app):

    @app.on_message(filters.command("system"))
    async def system_handler(client, message):

        text = get_system_text()

        try:

            if SYSTEM_IMAGE:

                sent = await message.reply_photo(
                    photo=SYSTEM_IMAGE,
                    caption=text,
                    parse_mode=ParseMode.HTML
                )

            else:

                sent = await message.reply_text(
                    text,
                    parse_mode=ParseMode.HTML
                )

            await asyncio.sleep(30)

            try:
                await sent.delete()
            except Exception:
                pass

        except Exception as e:

            try:
                await message.reply_text(
                    f"❌ <b>{smallcaps('System information error')}:</b>\n\n"
                    f"<code>{str(e)[:1000]}</code>",
                    parse_mode=ParseMode.HTML
                )
            except Exception:
                pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #