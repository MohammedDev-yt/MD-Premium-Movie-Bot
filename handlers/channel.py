# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram import filters
from config import ADMIN_IDS
import database

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def register_channel_handlers(app):

    @app.on_message(
        filters.command("channel") & filters.user(list(ADMIN_IDS))
    )
    async def channel_command(client, message):

        try:
            # Make sure database is initialized
            if database.chats_collection is None:
                await message.reply_text(
                    " <b>Database is not initialized.</b>\n\n"
                    "<b>Please restart the bot and try again.</b>"
                )
                return

            groups = []

            # Get all saved chats
            async for chat in database.chats_collection.find({}):

                chat_id = chat.get("chat_id")

                if not chat_id:
                    continue

                # IMPORTANT:
                # database.py saves this as "chat_type"
                chat_type = str(
                    chat.get("chat_type", "")
                ).lower()

                # Only groups and supergroups
                if chat_type in ("group", "supergroup"):
                    groups.append(chat)

            # No groups found
            if not groups:
                await message.reply_text(
                    "📋 <b>TOTAL CONNECTED GROUPS</b>\n\n"
                    "📊 <b>›› Total:</b> 0\n\n"
                    "<b>❌ No connected groups found.</b>"
                )
                return

            # Sort groups alphabetically
            groups.sort(
                key=lambda x: str(
                    x.get("title") or x.get("name") or ""
                ).lower()
            )

            text = (
                " <b>TOTAL CONNECTED GROUPS</b>\n\n"
                f" <b>›› Total:</b> {len(groups)}\n\n"
            )

            # Build group list
            for number, chat in enumerate(groups, start=1):

                chat_id = chat.get("chat_id")
                title = (
                    chat.get("title")
                    or chat.get("name")
                    or "Unknown Group"
                )

                username = chat.get("username")

                if username:
                    text += (
                        f"<b>{number}. {title}</b>\n"
                        f"<b>›› 👤 @{username}</b>\n"
                        f"<b>››🆔 <code>{chat_id}</code></b>\n\n"
                    )
                else:
                    text += (
                        f"<b>›› {number}. {title}</b>\n"
                        f"<b>›› 🆔 <code>{chat_id}</code></b>\n\n"
                    )

            # Telegram message limit protection
            chunks = []

            while len(text) > 4000:

                split_at = text.rfind("\n\n", 0, 4000)

                if split_at == -1:
                    split_at = 4000

                chunks.append(text[:split_at])
                text = text[split_at:].lstrip()

            if text:
                chunks.append(text)

            # Send all chunks
            for chunk in chunks:
                await message.reply_text(chunk)

        except Exception as e:

            await message.reply_text(
                "❌ <b>Failed to get connected groups.</b>\n\n"
                f"<code>{str(e)}</code>"
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #