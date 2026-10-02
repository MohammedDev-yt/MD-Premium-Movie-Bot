# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from urllib.parse import quote_plus
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def register_share_handlers(app):

    @app.on_message(filters.command("share"))
    async def share_handler(client, message):

        if len(message.command) < 2:
            return await message.reply_text(
                "❌ <b>Usage:</b>\n\n"
                "<code>/share Hello everyone!</code>"
            )

        text = message.text.split(
            None,
            1
        )[1].strip()

        if not text:
            return await message.reply_text(
                "❌ <b>Please provide some text.</b>"
            )

        share_url = (
            "https://t.me/share/url"
            f"?url=&text={quote_plus(text)}"
        )

        await message.reply_text(
            "🔗 <b>Share Text</b>\n\n"
            f"📝 {text}\n\n"
            "Click the button below to share it.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Sʜᴀʀᴇ Tᴇxᴛ •",
                            url=share_url
                        )
                    ]
                ]
            )
        )
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #