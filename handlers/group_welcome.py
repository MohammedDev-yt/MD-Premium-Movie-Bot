# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

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

from config import UPDATES_CHANNEL
from database import register_chat

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# GROUP WELCOME HANDLER
# ============================================================

def register_group_welcome_handlers(app):

    @app.on_message(filters.new_chat_members)
    async def bot_added_to_group(client, message):

        try:
            # ------------------------------------------------
            # GROUP INFORMATION
            # ------------------------------------------------

            chat = message.chat

            chat_id = chat.id
            group_name = chat.title or "this group"

            # ------------------------------------------------
            # CHECK WHETHER THE BOT WAS ADDED
            # ------------------------------------------------

            me = await client.get_me()

            bot_added = False

            for member in message.new_chat_members:
                if member.id == me.id:
                    bot_added = True
                    break

            # ------------------------------------------------
            # IF BOT WAS ADDED
            # ------------------------------------------------

            if bot_added:

                # ------------------------------------------------
                # GROUP INFORMATION
                # ------------------------------------------------

                chat_type = str(chat.type.value)

                # ------------------------------------------------
                # SAVE GROUP TO MONGODB
                # ------------------------------------------------

                await register_chat(
                    chat_id=chat_id,
                    chat_type=chat_type,
                    title=group_name
                )

                print(
                    f"GROUP REGISTERED | "
                    f"TITLE={group_name} | "
                    f"ID={chat_id} | "
                    f"TYPE={chat_type}"
                )

                # ------------------------------------------------
                # SUPPORT / UPDATES LINKS
                # ------------------------------------------------

                support_url = "https://t.me/Coders_Grp"
                updates_url = "https://t.me/Aero_Unity"

                if UPDATES_CHANNEL:

                    updates_username = (
                        str(UPDATES_CHANNEL)
                        .replace("https://t.me/", "")
                        .replace("http://t.me/", "")
                        .replace("@", "")
                        .strip("/")
                    )

                    if updates_username:
                        updates_url = (
                            f"https://t.me/{updates_username}"
                        )

                # ------------------------------------------------
                # WELCOME TEXT
                # ------------------------------------------------

                text = (
                    f"<b>Thankyou For Adding Me In "
                    f"{group_name}</b> ❣️\n\n"
                    "<b>If you have any questions & doubts</b>\n"
                    "<b>about using me contact support.</b>"
                )

                # ------------------------------------------------
                # BUTTONS
                # ------------------------------------------------

                buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "• Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ •",
                                url=support_url
                            ),
                            InlineKeyboardButton(
                                "• Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ •",
                                url=updates_url
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "• Bᴏᴛ Oᴡɴᴇʀ •",
                                url="https://t.me/Mr_Mohammed_29"
                            )
                        ]
                    ]
                )

                # ------------------------------------------------
                # SEND BOT ADDED MESSAGE
                # ------------------------------------------------

                await message.reply_text(
                    text,
                    reply_markup=buttons
                )

                return

            # ====================================================
            # NORMAL USER JOINED
            # ====================================================

            for member in message.new_chat_members:

                # Don't welcome other bots
                if member.is_bot:
                    continue

                # ------------------------------------------------
                # USER NAME
                # ------------------------------------------------

                first_name = member.first_name or "User"

                # ------------------------------------------------
                # UPDATES LINK
                # ------------------------------------------------

                updates_url = "https://t.me/Aero_Unity"

                if UPDATES_CHANNEL:

                    updates_username = (
                        str(UPDATES_CHANNEL)
                        .replace("https://t.me/", "")
                        .replace("http://t.me/", "")
                        .replace("@", "")
                        .strip("/")
                    )

                    if updates_username:
                        updates_url = (
                            f"https://t.me/{updates_username}"
                        )

                # ------------------------------------------------
                # USER WELCOME BUTTON
                # ------------------------------------------------

                user_buttons = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "• Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ •",
                                url=updates_url
                            )
                        ]
                    ]
                )

                # ------------------------------------------------
                # USER WELCOME MESSAGE
                # ------------------------------------------------

                welcome_text = (
                    f"✨ <b>Wᴇʟᴄᴏᴍᴇ {first_name}!</b> 👋\n\n"
                    f"<b>Wᴇʟᴄᴏᴍᴇ Tᴏ {group_name}!</b>\n\n"
                    f"👤 Hᴇʏ <b>{first_name}</b>, "
                    "<b>glad to have you here! ❤️</b>\n"
                    "<b>search unlimited movies, series, animes, dramas, TV serials.</b>\n"
                    "<b>Maintained By : @Mr_Mohammed_29</b>"
                )

                # ------------------------------------------------
                # SEND GIF + WELCOME
                # ------------------------------------------------

                try:

                    await message.reply_animation(
                        animation="CgACAgUAAxkBAAIFR2qbmMVdmim8I1Ft0vzSrmkOqN2eAALYFwAC-EmIVDVrUMvRuMVUHgQ",
                        caption=welcome_text,
                        reply_markup=user_buttons
                    )

                except Exception as gif_error:

                    print(
                        f"WELCOME GIF ERROR: {gif_error}"
                    )

                    # ------------------------------------------------
                    # FALLBACK: SEND TEXT WELCOME
                    # ------------------------------------------------

                    await message.reply_text(
                        welcome_text,
                        reply_markup=user_buttons
                    )

        except Exception as e:

            print(
                f"GROUP WELCOME ERROR: {e}"
                        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #