# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import logging
import os
from html import escape

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram import filters, enums, StopPropagation
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


from config import OWNER_ID, ADMIN_IDS

from database import (
    get_fsub_channels,
    add_fsub_channel,
    remove_fsub_channel
)


logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# ADMIN CHECK
# ============================================================

def is_admin(user_id):
    return (
        user_id == OWNER_ID
        or user_id in ADMIN_IDS
    )


admin_only = filters.create(
    lambda _, __, message: (
        message.from_user is not None
        and is_admin(message.from_user.id)
    )
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# CHECK USER JOIN STATUS
# ============================================================

async def check_user_joined(
    client,
    user_id,
    channel
):
    try:

        member = await client.get_chat_member(
            channel["chat_id"],
            user_id
        )

        status = member.status

        if status in [
            enums.ChatMemberStatus.OWNER,
            enums.ChatMemberStatus.ADMINISTRATOR,
            enums.ChatMemberStatus.MEMBER
        ]:
            return True

        if (
            status == enums.ChatMemberStatus.RESTRICTED
            and getattr(member, "is_member", False)
        ):
            return True

        return False

    except Exception as e:

        logger.warning(
            "FSub check failed | user=%s | channel=%s | error=%s",
            user_id,
            channel.get("chat_id"),
            e
        )

        return False

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# CHECK ALL FSUB CHANNELS
# ============================================================

async def check_all_fsubs(
    client,
    user_id
):

    channels = await get_fsub_channels()

    not_joined = []

    for channel in channels:

        joined = await check_user_joined(
            client,
            user_id,
            channel
        )

        if not joined:
            not_joined.append(channel)

    return not_joined


# ============================================================
# FSUB KEYBOARD
# ============================================================

def build_fsub_keyboard(
    channels,
    check_data="fsub_check"
):

    buttons = []

    for channel in channels:

        title = channel.get(
            "title",
            "Join Channel"
        )

        invite_link = channel.get(
            "invite_link"
        )

        username = channel.get(
            "username"
        )

        if invite_link:

            link = invite_link

        elif username:

            username = username.lstrip("@")

            link = f"https://t.me/{username}"

        else:

            continue

        buttons.append([
            InlineKeyboardButton(
                f"• Join {title} •",
                url=link
            )
        ])

    # --------------------------------------------------------
    # TRY AGAIN
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "• ᴛʀʏ ᴀɢᴀɪɴ •",
            callback_data=check_data
        )
    ])

    return InlineKeyboardMarkup(
        buttons
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FSUB MESSAGE
# ============================================================

async def send_fsub_message(
    client,
    message,
    channels=None,
    deep_link=None
):

    user = message.from_user

    if not user:
        return None
        
    if channels is None:

        channels = await check_all_fsubs(
            client,
            user.id
        )

    if not channels:
        return None

    first_name = escape(
        user.first_name or "User"
    )

    clickable_name = (
        f'<a href="tg://user?id={user.id}">'
        f'{first_name}'
        f'</a>'
    )

    text = (
        f"<b>ʜᴇʏ {clickable_name}</b> ♡\n\n"

        "<b>›› ‼️ ʟᴏᴏᴋs ʟɪᴋᴇ ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ "
        "ᴊᴏɪɴᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, "
        "sᴜʙsᴄʀɪʙᴇ ɴᴏᴡ...</b>\n\n"
    )
    
    # --------------------------------------------------------
    # PRESERVE ORIGINAL REQUEST
    # --------------------------------------------------------

    if deep_link:

        check_data = (
            f"fsub_check_{deep_link}"
        )

    else:

        check_data = "fsub_check"

    keyboard = build_fsub_keyboard(
        channels,
        check_data=check_data
    )

    image = os.getenv(
        "FSUB_IMAGE_URL",
        ""
    ).strip()

    if image:

        return await message.reply_photo(
            photo=image,
            caption=text,
            reply_markup=keyboard
        )

    return await message.reply_text(
        text,
        reply_markup=keyboard
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# /START FORCE SUBSCRIBE CHECK
# ============================================================

def register_fsub_start_handler(app):

    @app.on_message(
        filters.command("start"),
        group=-1
    )
    async def fsub_start_handler(
        client,
        message
    ):

        if not message.from_user:
            return

        # ----------------------------------------------------
        # FSUB ONLY IN PRIVATE CHAT
        # ----------------------------------------------------

        if message.chat.type != enums.ChatType.PRIVATE:
            return

        user_id = message.from_user.id

        # ----------------------------------------------------
        # GET CHANNELS
        # ----------------------------------------------------

        channels = await get_fsub_channels()

        if not channels:
            return

        # ----------------------------------------------------
        # CHECK MEMBERSHIP
        # ----------------------------------------------------

        not_joined = await check_all_fsubs(
            client,
            user_id
        )

        # ----------------------------------------------------
        # ALREADY JOINED EVERYTHING
        # ----------------------------------------------------

        if not not_joined:
            return

        # ----------------------------------------------------
        # GET ORIGINAL DEEP LINK
        # ----------------------------------------------------

        deep_link = None

        if (
            message.command
            and len(message.command) >= 2
        ):

            payload = message.command[1].strip()

            if payload:
                deep_link = payload

        # ----------------------------------------------------
        # SEND FSUB MESSAGE
        # ----------------------------------------------------

        await send_fsub_message(
            client,
            message,
            not_joined,
            deep_link=deep_link
        )

        # ----------------------------------------------------
        # STOP NORMAL START HANDLER
        # ----------------------------------------------------

        raise StopPropagation

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# TRY AGAIN CALLBACK
# ============================================================

def register_fsub_callback_handler(app):

    @app.on_callback_query(
        filters.regex(r"^fsub_check(?:_.+)?$")
    )
    async def fsub_check_callback(
        client,
        callback_query
    ):

        user_id = callback_query.from_user.id

        # ----------------------------------------------------
        # ONLY PM
        # ----------------------------------------------------

        if (
            not callback_query.message
            or callback_query.message.chat.type
            != enums.ChatType.PRIVATE
        ):

            await callback_query.answer(
                "❌ Please check your subscription in PM.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # GET CALLBACK DATA
        # ----------------------------------------------------

        callback_data = (
            callback_query.data
            or ""
        )

        deep_link = None

        prefix = "fsub_check_"

        if callback_data.startswith(prefix):

            deep_link = callback_data[
                len(prefix):
            ].strip()

            if not deep_link:
                deep_link = None

        # ----------------------------------------------------
        # GET CHANNELS
        # ----------------------------------------------------

        channels = await get_fsub_channels()

        if not channels:

            await callback_query.answer(
                "✅ No Force Subscribe channels configured.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # CHECK MEMBERSHIP AGAIN
        # ----------------------------------------------------

        not_joined = await check_all_fsubs(
            client,
            user_id
        )

        # ====================================================
        # ALL CHANNELS JOINED
        # ====================================================

        if not not_joined:

            await callback_query.answer(
                "✅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴠᴇʀɪꜰɪᴇᴅ!",
                show_alert=True
            )

            # ------------------------------------------------
            # KEEP FSUB MESSAGE ALIVE WHILE REQUEST IS
            # PROCESSED.
            # ------------------------------------------------

            if deep_link:

                try:

                    # ========================================
                    # FILE REQUEST
                    # ========================================

                    if deep_link.startswith("file_"):

                        try:

                            message_id = int(
                                deep_link.split(
                                    "_",
                                    1
                                )[1]
                            )

                        except (
                            ValueError,
                            IndexError
                        ):

                            await client.send_message(
                                user_id,
                                "❌ Invalid file request."
                            )

                            return

                        # ------------------------------------
                        # Local import avoids circular import
                        # ------------------------------------

                        from handlers.search import (
                            handle_file_deep_link
                        )

                        await handle_file_deep_link(
                            client=client,
                            message=callback_query.message,
                            message_id=message_id,
                            user_id=user_id
                        )

                    # ========================================
                    # SEND ALL REQUEST
                    # ========================================

                    elif deep_link.startswith("sendall_"):

                        parts = deep_link.split("_")

                        if len(parts) != 3:

                            await client.send_message(
                                user_id,
                                "❌ Invalid Send All request."
                            )

                            return

                        session_id = parts[1]

                        try:

                            page = int(
                                parts[2]
                            )

                        except ValueError:

                            await client.send_message(
                                user_id,
                                "❌ Invalid Send All page."
                            )

                            return

                        # ------------------------------------
                        # Local import avoids circular import
                        # ------------------------------------

                        from handlers.search import (
                            handle_sendall_deep_link
                        )

                        await handle_sendall_deep_link(
                            client=client,
                            message=callback_query.message,
                            session_id=session_id,
                            page=page,
                            user_id=user_id
                        )
                        
                    # ========================================
                    # PERMANENT LINK REQUEST
                    # ========================================

                    elif deep_link.startswith(
                        ("pl_", "ba_", "pb_")
                    ):

                        from handlers.permanent_links import (
                            handle_permanent_link
                        )

                        await handle_permanent_link(
                            client=client,
                            message=callback_query.message,
                            token=deep_link,
                            user_id=user_id
                        )

                    # ========================================
                    # UNKNOWN REQUEST
                    # ========================================

                    else:

                        await client.send_message(
                            user_id,
                            "❌ Invalid request link."
                        )

                        return

                except Exception as e:

                    logger.exception(
                        "Failed to resume original request | "
                        "user=%s | deep_link=%s",
                        user_id,
                        deep_link
                    )

                    try:

                        await client.send_message(
                            user_id,
                            "❌ Something went wrong while "
                            "processing your request."
                        )

                    except Exception:

                        pass

                    return

                # ------------------------------------------------
                # REQUEST COMPLETED
                # NOW DELETE FSUB MESSAGE
                # ------------------------------------------------

                try:

                    await callback_query.message.delete()

                except Exception as e:

                    logger.debug(
                        "Could not delete FSub message "
                        "after request: %s",
                        e
                    )

                return

            # ------------------------------------------------
            # NORMAL /START
            # ------------------------------------------------

            try:

                await callback_query.message.delete()

            except Exception as e:

                logger.debug(
                    "Could not delete FSub message: %s",
                    e
                )

            await client.send_message(
                user_id,
                "/start"
            )

            return

        # ====================================================
        # STILL NOT JOINED
        # ====================================================

        await callback_query.answer(
            "›› ʏᴏᴜ ʜᴀᴠᴇɴ'ᴛ ᴊᴏɪɴᴇᴅ ᴛᴏ ᴏᴜʀ ᴄʜᴀɴɴᴇʟs ʏᴇᴛ, sᴜʙsᴄʀɪʙᴇ ɴᴏw.",
            show_alert=True
        )

        # ----------------------------------------------------
        # SHOW ONLY CHANNELS NOT YET JOINED
        # ----------------------------------------------------

        if deep_link:

            check_data = (
                f"fsub_check_{deep_link}"
            )

        else:

            check_data = "fsub_check"

        keyboard = build_fsub_keyboard(
            not_joined,
            check_data=check_data
        )

        try:

            await callback_query.message.edit_reply_markup(
                reply_markup=keyboard
            )

        except Exception as e:

            logger.debug(
                "Could not update FSub keyboard: %s",
                e
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# ADMIN FORCE SUBSCRIBE
# ============================================================

def register_fsub_admin_handlers(app):

    @app.on_message(
        filters.command("addfsub")
        & admin_only
    )
    async def addfsub_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "<code>/addfsub @channel</code>\n\n"
                "<b>Private channel:</b>\n"
                "<code>/addfsub -1001234567890 "
                "https://t.me/+invite</code>"
            )

            return

        target = message.command[1]

        invite_link = None

        if len(message.command) >= 3:

            invite_link = message.command[2]

        try:

            chat = await client.get_chat(
                target
            )

        except Exception as e:

            await message.reply_text(
                "❌ <b>Could not find this channel\n\n"
                "Make sure the bot is inside the channel "
                "and has the required permissions.</b>\n\n"
                f"<code>{e}</code>"
            )

            return

        # ----------------------------------------------------
        # CHANNEL CHECK
        # ----------------------------------------------------

        if chat.type not in [
            enums.ChatType.CHANNEL,
            enums.ChatType.SUPERGROUP
        ]:

            await message.reply_text(
                "❌ Please provide a channel or group."
            )

            return

        # ----------------------------------------------------
        # PUBLIC USERNAME
        # ----------------------------------------------------

        username = getattr(
            chat,
            "username",
            None
        )

        # ----------------------------------------------------
        # INVITE LINK
        # ----------------------------------------------------

        if not invite_link and username:

            invite_link = (
                f"https://t.me/{username}"
            )

        # ----------------------------------------------------
        # PRIVATE CHANNEL
        # ----------------------------------------------------

        if not invite_link:

            try:

                invite_link = (
                    await client.export_chat_invite_link(
                        chat.id
                    )
                )

            except Exception as e:

                await message.reply_text(
                    "❌ <b>Could not create an invite link.</b>\n\n"
                    "For a private channel, send the invite link "
                    "with the command:\n\n"
                    "<code>/addfsub -1001234567890 "
                    "https://t.me/+xxxx</code>\n\n"
                    f"<code>{e}</code>"
                )

                return

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        channel_data = {

            "chat_id": chat.id,

            "title": (
                chat.title
                or "Join Channel"
            ),

            "username": username,

            "invite_link": invite_link
        }

        success = await add_fsub_channel(
            channel_data
        )

        if not success:

            await message.reply_text(
                "<b>Tʜɪs Cʜᴀɴɴᴇʟ Is Aʟʀᴇᴀᴅʏ Iɴ Tʜᴇ Fᴏʀᴄᴇ Sᴜʙ Lɪsᴛ</b>"
            )

            return

        await message.reply_text(
            "✅ <b>Fᴏʀᴄᴇ Cʜᴀɴɴᴇʟ Aᴅᴅᴇᴅ</b>\n\n"

            f"<b>›› Cʜᴀɴɴᴇʟ Nᴀᴍᴇ:</b> "
            f"{chat.title}\n"

            f"<b>›› Cʜᴀɴɴᴇʟ ID:</b> "
            f"<code>{chat.id}</code>\n\n"

            f"<b>›› Cʜᴀɴɴᴇʟ Lɪɴᴋ:</b> "
            f"{invite_link}"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# /DELFSUB
# ============================================================

def register_fsub_delete_handler(app):

    @app.on_message(
        filters.command("delfsub")
        & admin_only
    )
    async def delfsub_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "<code>/delfsub @channel</code>\n\n"
                "or\n\n"
                "<code>/delfsub -1001234567890</code>"
            )

            return

        target = message.command[1]

        try:

            chat = await client.get_chat(
                target
            )

            chat_id = chat.id

        except Exception:

            try:

                chat_id = int(target)

            except ValueError:

                await message.reply_text(
                    "❌ Invalid channel."
                )

                return

        removed = await remove_fsub_channel(
            chat_id
        )

        if not removed:

            await message.reply_text(
                "<b>Tʜɪs Cʜᴀɴɴᴇʟ Is Nᴏᴛ Iɴ Fᴏʀᴄᴇ Sᴜʙ Lɪsᴛ</b>"
            )

            return

        await message.reply_text(
            "✅ <b>Fᴏʀᴄᴇ Cʜᴀɴɴᴇʟ Rᴇᴍᴏᴠᴇᴅ</b>\n\n"
            f"<b>›› Cʜᴀɴɴᴇʟ ID : </b> "
            f"<code>{chat_id}</code>"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# /FSUBLIST
# ============================================================

def register_fsub_list_handler(app):

    @app.on_message(
        filters.command("fsublist")
        & admin_only
    )
    async def fsublist_handler(
        client,
        message
    ):

        channels = await get_fsub_channels()

        if not channels:

            await message.reply_text(
                "📢 <b>Fᴏʀᴄᴇ Cʜᴀɴɴᴇʟs Lɪsᴛ</b>\n\n"
                "<b>Nᴏ Cʜᴀɴɴᴇʟs Fᴏᴜɴᴅ!</b>"
            )

            return

        text = (
            "📢 <b>Fᴏʀᴄᴇ Cʜᴀɴɴᴇʟs Lɪsᴛ</b>\n\n"
        )

        for index, channel in enumerate(
            channels,
            start=1
        ):

            title = channel.get(
                "title",
                "Unknown"
            )

            username = channel.get(
                "username"
            )

            chat_id = channel.get(
                "chat_id"
            )

            text += (
                f"┎ <b>{index}. {title}</b>\n"
            )

            if username:

                text += (
                    f"┃ <b>›› Usᴇʀɴᴀᴍᴇ: </b>"
                    f"@{username.lstrip('@')}\n"
                )

            text += (
                f"┖ <b>›› ID:</b> <code>{chat_id}</code>\n\n"
            )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "• ᴄʟᴏsᴇ •",
                    callback_data="fsub_close"
                )
            ]
        ])

        image = os.getenv(
            "FSUB_IMAGE_URL",
            ""
        ).strip()

        if image:

            await message.reply_photo(
                photo=image,
                caption=text,
                reply_markup=keyboard
            )

        else:

            await message.reply_text(
                text,
                reply_markup=keyboard
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# CLOSE BUTTON
# ============================================================

def register_fsub_close_handler(app):

    @app.on_callback_query(
        filters.regex(r"^fsub_close$")
    )
    async def fsub_close_callback(
        client,
        callback_query
    ):

        await callback_query.answer()

        try:

            await callback_query.message.delete()

        except Exception:
            pass
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #


# ============================================================
# REGISTER EVERYTHING
# ============================================================

def register_fsub_handlers(app):

    register_fsub_start_handler(app)

    register_fsub_callback_handler(app)

    register_fsub_admin_handlers(app)

    register_fsub_delete_handler(app)

    register_fsub_list_handler(app)

    register_fsub_close_handler(app)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #