# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import asyncio
import logging
import re

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from html import escape
from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import (
    DATABASE_CHANNEL_ID,
    OWNER_ID
)

from handlers.fsub import (
    check_all_fsubs,
    send_fsub_message
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# CONFIG
# ============================================================

MAX_BATCH_FILES = 50
DELETE_AFTER = 300

UPDATES_URL = "https://t.me/Aero_Unity"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# OWNER CHECK
# ============================================================

def is_owner(message):
    try:
        return (
            message.from_user
            and int(message.from_user.id) == int(OWNER_ID)
        )
    except Exception:
        return False

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def owner_required(message):
    if not is_owner(message):
        await message.reply_text(
            "❌ <b>Only the Owner can use this command.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return False

    return True

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# DELETE MESSAGE AFTER 5 MINUTES
# ============================================================

async def delete_after_5_minutes(
    client,
    chat_id,
    message_id
):

    try:

        await asyncio.sleep(DELETE_AFTER)

        try:

            await client.delete_messages(
                chat_id,
                message_id
            )

            logger.info(
                "PERMANENT FILE/WARNING DELETED | "
                "chat=%s | message=%s",
                chat_id,
                message_id
            )

        except Exception as e:

            logger.warning(
                "Failed to delete message | "
                "chat=%s | message=%s | error=%s",
                chat_id,
                message_id,
                e
            )

    except asyncio.CancelledError:

        pass

    except Exception as e:

        logger.warning(
            "Delete timer error | %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# MESSAGE / LINK HELPERS
# ============================================================

def get_message_id_from_link(text):

    if not text:
        return None

    text = text.strip()

    match = re.search(
        r"(?:https?://)?t\.me/c/(\d+)/(\d+)",
        text
    )

    if match:

        channel_number = match.group(1)
        message_id = int(match.group(2))

        channel_id = int(
            "-100" + channel_number
        )

        return channel_id, message_id

    match = re.search(
        r"(?:https?://)?t\.me/([A-Za-z0-9_]+)/(\d+)",
        text
    )

    if match:

        username = match.group(1)
        message_id = int(match.group(2))

        return username, message_id

    return None
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def parse_message_reference(value):

    if not value:
        return None

    value = value.strip()

    if value.isdigit():

        return (
            DATABASE_CHANNEL_ID,
            int(value)
        )

    return get_message_id_from_link(value)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def make_single_token(message_id):

    return f"pl_{message_id}"
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def make_batch_token(
    first_id,
    last_id,
    protected=False
):

    prefix = (
        "pb_"
        if protected
        else "ba_"
    )

    return (
        f"{prefix}"
        f"{first_id}_"
        f"{last_id}"
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def make_start_link(
    client,
    token
):

    try:

        me = await client.get_me()

        if not me.username:
            return None

        return (
            f"https://t.me/"
            f"{me.username}"
            f"?start={token}"
        )

    except Exception as e:

        logger.error(
            "Failed to create start link: %s",
            e
        )

        return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FORWARDED MESSAGE ORIGINAL SOURCE
# ============================================================

def get_original_message_reference(
    message
):

    original_chat_id = None
    original_message_id = None

    try:

        forward_origin = getattr(
            message,
            "forward_origin",
            None
        )

        if forward_origin:

            original_message_id = getattr(
                forward_origin,
                "message_id",
                None
            )

            origin_chat = getattr(
                forward_origin,
                "chat",
                None
            )

            if origin_chat:

                original_chat_id = getattr(
                    origin_chat,
                    "id",
                    None
                )

    except Exception as e:

        logger.warning(
            "forward_origin read failed: %s",
            e
        )

    if not original_message_id:

        original_message_id = getattr(
            message,
            "forward_from_message_id",
            None
        )

    if not original_chat_id:

        forward_chat = getattr(
            message,
            "forward_from_chat",
            None
        )

        if forward_chat:

            original_chat_id = getattr(
                forward_chat,
                "id",
                None
            )

    if not original_message_id:

        return None

    return (
        original_chat_id,
        int(original_message_id)
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# DATABASE MESSAGE
# ============================================================

async def get_database_message(
    client,
    message_id
):

    try:

        message = await client.get_messages(
            DATABASE_CHANNEL_ID,
            int(message_id)
        )

        if not message:
            return None

        if getattr(
            message,
            "empty",
            False
        ):

            return None

        return message

    except Exception as e:

        logger.error(
            "Failed to get database message "
            "%s: %s",
            message_id,
            e
        )

        return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# MEDIA CHECK
# ============================================================

def has_supported_media(message):

    if not message:
        return False

    return any(
        [
            message.document,
            message.video,
            message.audio,
            message.animation,
            message.voice,
            message.photo
        ]
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILE CAPTION
# ============================================================

def build_file_caption(
    database_message
):

    original_caption = (
        getattr(
            database_message,
            "caption",
            None
        )
        or ""
    ).strip()

    if original_caption:

        safe_caption = escape(
            original_caption
        )

        # The actual file caption/title itself
        # is clickable and opens the Updates channel.
        return (
            f'<b><a href="{UPDATES_URL}">'
            f'{safe_caption}'
            f'</a></b>'
        )

    return (
        f'<b><a href="{UPDATES_URL}">'
        f'📁 Yᴏᴜʀ Rᴇǫᴜᴇsᴛᴇᴅ Fɪʟᴇ'
        f'</a></b>'
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILE KEYBOARD
# ============================================================

def build_file_keyboard():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "• Uᴘᴅᴀᴛᴇs •",
                    url=UPDATES_URL
                )
            ]
        ]
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEND ONE PERMANENT FILE
# ============================================================

async def send_permanent_file(
    client,
    user_id,
    message_id,
    protected=False
):

    database_message = (
        await get_database_message(
            client,
            message_id
        )
    )

    if not database_message:
        return False

    if not has_supported_media(
        database_message
    ):

        return False

    try:

        caption = build_file_caption(
            database_message
        )

        sent_message = await client.copy_message(
            chat_id=user_id,
            from_chat_id=DATABASE_CHANNEL_ID,
            message_id=database_message.id,
            caption=caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_file_keyboard(),
            protect_content=protected
        )

        # ----------------------------------------------------
        # DELETE FILE AFTER 5 MINUTES
        # ----------------------------------------------------

        if sent_message:

            asyncio.create_task(
                delete_after_5_minutes(
                    client,
                    user_id,
                    sent_message.id
                )
            )

        logger.info(
            "PERMANENT FILE SENT | "
            "user=%s | message_id=%s | protected=%s",
            user_id,
            message_id,
            protected
        )

        return True

    except Exception as e:

        logger.error(
            "PERMANENT FILE SEND ERROR | "
            "user=%s | message_id=%s | error=%s",
            user_id,
            message_id,
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
# SEND WARNING
# ============================================================

async def send_delete_warning(
    client,
    user_id,
    batch=False
):

    if batch:

        text = (
            "<b>⌛ Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ Iѕѕᴜᴇѕ...</b>\n\n"
            "<b>» Yᴏᴜʀ Fɪʟᴇѕ Wɪʟʟ Bᴇ Dᴇʟᴇᴛᴇᴅ Wɪᴛʜɪɴ 5 Mɪɴ\n"
            "Sᴏ Pʟᴇᴀѕᴇ Fᴏʀᴡᴀʀᴅ Tʜᴇᴍ Tᴏ Aɴʏ Oᴛʜᴇʀ\n"
            "Pʟᴀᴄᴇ Oʀ Sᴀᴠᴇᴅ Mᴇѕѕᴀɢᴇѕ Fᴏʀ Fᴜᴛᴜʀᴇ\n"
            "Aᴠᴀɪʟᴀʙɪʟɪᴛʏ</b>\n\n\n"
            "<b>Nᴏᴛᴇ : Uѕᴇ VLC Pʟᴀʏᴇʀ Oʀ MX Pʟᴀʏᴇʀ\n"
            "Tᴏ Wᴀᴛᴄʜ Tʜᴇ Eᴘɪѕᴏᴅᴇѕ Wɪᴛʜ Gᴏᴏᴅ\n"
            "Exᴘᴇʀɪᴇɴᴄᴇ</b>"
        )

    else:

        text = (
            "<b>⌛ Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ Iѕѕᴜᴇѕ...</b>\n\n"
            "<b>» Yᴏᴜʀ Fɪʟᴇ Wɪʟʟ Bᴇ Dᴇʟᴇᴛᴇᴅ Wɪᴛʜɪɴ 5 Mɪɴ\n"
            "Sᴏ Pʟᴇᴀѕᴇ Fᴏʀᴡᴀʀᴅ Iᴛ Tᴏ Aɴʏ Oᴛʜᴇʀ\n"
            "Pʟᴀᴄᴇ Oʀ Sᴀᴠᴇᴅ Mᴇѕѕᴀɢᴇѕ Fᴏʀ Fᴜᴛᴜʀᴇ\n"
            "Aᴠᴀɪʟᴀʙɪʟɪᴛʏ</b>\n\n\n"
            "<b>Nᴏᴛᴇ : Uѕᴇ VLC Pʟᴀʏᴇʀ Oʀ MX Pʟᴀʏᴇʀ\n"
            "Tᴏ Wᴀᴛᴄʜ Tʜᴇ Eᴘɪѕᴏᴅᴇ Wɪᴛʜ Gᴏᴏᴅ\n"
            "Exᴘᴇʀɪᴇɴᴄᴇ</b>"
        )

    try:

        warning = await client.send_message(
            user_id,
            text,
            parse_mode=enums.ParseMode.HTML
        )

        # ----------------------------------------------------
        # DELETE WARNING AFTER 5 MINUTES
        # ----------------------------------------------------

        if warning:

            asyncio.create_task(
                delete_after_5_minutes(
                    client,
                    user_id,
                    warning.id
                )
            )

        return warning

    except Exception as e:

        logger.warning(
            "Failed to send delete warning | "
            "user=%s | error=%s",
            user_id,
            e
        )

        return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEND BATCH
# ============================================================

async def send_permanent_batch(
    client,
    user_id,
    first_id,
    last_id,
    protected=False
):

    if first_id > last_id:

        first_id, last_id = (
            last_id,
            first_id
        )

    total = (
        last_id
        - first_id
        + 1
    )

    if total > MAX_BATCH_FILES:

        return 0, True

    sent = 0

    for message_id in range(
        first_id,
        last_id + 1
    ):

        success = (
            await send_permanent_file(
                client=client,
                user_id=user_id,
                message_id=message_id,
                protected=protected
            )
        )

        if success:

            sent += 1

    return sent, False

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# HANDLE PERMANENT LINK
# ============================================================

async def handle_permanent_link(
    client,
    message,
    token,
    user_id=None
):

    if not user_id:

        if not message.from_user:
            return

        user_id = message.from_user.id

    if not token:
        return

    token = token.strip()

    # ========================================================
    # FORCE SUB CHECK
    # ========================================================

    not_joined = await check_all_fsubs(
        client,
        user_id
    )

    if not_joined:

        await send_fsub_message(
            client,
            message,
            not_joined,
            deep_link=token
        )

        return

    # ========================================================
    # SINGLE PROTECTED LINK
    # ========================================================

    if token.startswith("pl_"):

        raw_id = token[3:]

        if not raw_id.isdigit():

            await client.send_message(
                user_id,
                "❌ <b>Invalid permanent link.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        message_id = int(raw_id)

        success = (
            await send_permanent_file(
                client=client,
                user_id=user_id,
                message_id=message_id,
                protected=True
            )
        )

        if not success:

            await client.send_message(
                user_id,
                "❌ <b>File not found or unavailable.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        # Warning comes AFTER the file
        await send_delete_warning(
            client,
            user_id,
            batch=False
        )

        return

    # ========================================================
    # NORMAL BATCH
    # ========================================================

    if token.startswith("ba_"):

        parts = token[3:].split("_")

        if (
            len(parts) != 2
            or not all(
                part.isdigit()
                for part in parts
            )
        ):

            await client.send_message(
                user_id,
                "❌ <b>Invalid batch link.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        first_id = int(parts[0])
        last_id = int(parts[1])

        sent, too_many = (
            await send_permanent_batch(
                client=client,
                user_id=user_id,
                first_id=first_id,
                last_id=last_id,
                protected=False
            )
        )

        if too_many:

            await client.send_message(
                user_id,
                (
                    "❌ <b>Batch too large.</b>\n\n"
                    f"Maximum allowed: "
                    f"<b>{MAX_BATCH_FILES}</b> files."
                ),
                parse_mode=enums.ParseMode.HTML
            )

            return

        if sent == 0:

            await client.send_message(
                user_id,
                "❌ <b>No files were found in this batch.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        # Warning comes AFTER all batch files
        await send_delete_warning(
            client,
            user_id,
            batch=True
        )

        return

    # ========================================================
    # PROTECTED BATCH
    # ========================================================

    if token.startswith("pb_"):

        parts = token[3:].split("_")

        if (
            len(parts) != 2
            or not all(
                part.isdigit()
                for part in parts
            )
        ):

            await client.send_message(
                user_id,
                "❌ <b>Invalid protected batch link.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        first_id = int(parts[0])
        last_id = int(parts[1])

        sent, too_many = (
            await send_permanent_batch(
                client=client,
                user_id=user_id,
                first_id=first_id,
                last_id=last_id,
                protected=True
            )
        )

        if too_many:

            await client.send_message(
                user_id,
                (
                    "❌ <b>Batch too large.</b>\n\n"
                    f"Maximum allowed: "
                    f"<b>{MAX_BATCH_FILES}</b> files."
                ),
                parse_mode=enums.ParseMode.HTML
            )

            return

        if sent == 0:

            await client.send_message(
                user_id,
                "❌ <b>No files were found in this batch.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        # Warning comes AFTER all protected batch files
        await send_delete_warning(
            client,
            user_id,
            batch=True
        )

        return

    # ========================================================
    # UNKNOWN TOKEN
    # ========================================================

    await client.send_message(
        user_id,
        "❌ <b>Invalid or expired permanent link.</b>",
        parse_mode=enums.ParseMode.HTML
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# /PLINK
# OWNER ONLY
# ============================================================

async def plink_handler(
    client,
    message
):

    if not await owner_required(message):
        return

    if not message.reply_to_message:

        await message.reply_text(
            (
                "❌ <b>Reply to a media message "
                "with /plink.</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    replied = message.reply_to_message

    original_chat_id = None
    original_message_id = None

    # ========================================================
    # DIRECT DATABASE CHANNEL
    # ========================================================

    if str(message.chat.id) == str(
        DATABASE_CHANNEL_ID
    ):

        original_chat_id = DATABASE_CHANNEL_ID
        original_message_id = replied.id

    # ========================================================
    # FORWARDED DATABASE MESSAGE IN BOT PM
    # ========================================================

    else:

        reference = (
            get_original_message_reference(
                replied
            )
        )

        if reference:

            (
                original_chat_id,
                original_message_id
            ) = reference

    # ========================================================
    # CHECK ORIGINAL MESSAGE
    # ========================================================

    if not original_message_id:

        await message.reply_text(
            (
                "❌ <b>Could not find the original "
                "Database message.</b>\n\n"
                "Forward a file from the Database channel "
                "and reply to it with <code>/plink</code>."
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # DATABASE CHANNEL CHECK
    # ========================================================

    if str(original_chat_id) != str(
        DATABASE_CHANNEL_ID
    ):

        await message.reply_text(
            (
                "❌ <b>This file is not from "
                "the Database channel.</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # GET ORIGINAL MESSAGE
    # ========================================================

    database_message = (
        await get_database_message(
            client,
            original_message_id
        )
    )

    if not database_message:

        await message.reply_text(
            (
                "❌ <b>Original Database message "
                "was not found.</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # MEDIA CHECK
    # ========================================================

    if not has_supported_media(
        database_message
    ):

        await message.reply_text(
            (
                "❌ <b>Reply to a supported media file.</b>\n\n"
                "Supported: Video, Document, Audio, Photo."
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # CREATE LINK
    # ========================================================

    token = make_single_token(
        original_message_id
    )

    link = await make_start_link(
        client,
        token
    )

    if not link:

        await message.reply_text(
            "❌ <b>Bot username is not available.</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # SEND RESULT
    # ========================================================

    await message.reply_text(
        (
            "🔗 <b>Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
            f"🔗 <b><a href=\"{link}\">Oᴘᴇɴ Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ</a></b>\n\n"
            f"<b>Powered By: "
            f"<a href=\"{UPDATES_URL}\">Aᴇʀᴏ Uɴɪᴛʏ</a></b>"
        ),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Uᴘᴅᴀᴛᴇs •",
                        url=UPDATES_URL
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

# ============================================================
# GET BATCH REFERENCE
# ============================================================

def get_batch_reply_reference(
    replied
):

    if not replied:
        return None

    reference = (
        get_original_message_reference(
            replied
        )
    )

    if not reference:
        return None

    original_chat_id, original_message_id = (
        reference
    )

    if str(original_chat_id) != str(
        DATABASE_CHANNEL_ID
    ):

        return None

    return int(original_message_id)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# GENERATE BATCH LINK
# ============================================================

async def generate_batch_link(
    client,
    message,
    protected=False
):

    if not await owner_required(message):
        return

    text = (
        message.text
        or message.caption
        or ""
    )

    command_parts = text.split()

    command_name = (
        "pbatch"
        if protected
        else "batch"
    )

    # ========================================================
    # REPLY TO FORWARDED FILE METHOD
    # ========================================================

    replied = message.reply_to_message

    if replied:

        first_id = (
            get_batch_reply_reference(
                replied
            )
        )

        if first_id:

            if len(command_parts) == 2:

                last_ref = (
                    parse_message_reference(
                        command_parts[1]
                    )
                )

                if not last_ref:

                    await message.reply_text(
                        "❌ <b>Invalid last message.</b>",
                        parse_mode=enums.ParseMode.HTML
                    )

                    return

                last_chat, last_id = last_ref

                if str(last_chat) != str(
                    DATABASE_CHANNEL_ID
                ):

                    await message.reply_text(
                        (
                            "❌ <b>The last message "
                            "must be from the Database channel.</b>"
                        ),
                        parse_mode=enums.ParseMode.HTML
                    )

                    return

            else:

                await message.reply_text(
                    (
                        f"❌ <b>Reply to the first Database "
                        f"file and use:</b>\n\n"
                        f"<code>/{command_name} LAST_ID</code>\n\n"
                        f"<b>Example:</b>\n"
                        f"<code>/{command_name} 120</code>"
                    ),
                    parse_mode=enums.ParseMode.HTML
                )

                return

        else:

            first_id = None

    else:

        first_id = None

    # ========================================================
    # NORMAL TWO-REFERENCE METHOD
    # ========================================================

    if first_id is None:

        if len(command_parts) != 3:

            await message.reply_text(
                (
                    "❌ <b>Invalid format.</b>\n\n"
                    f"Use:\n"
                    f"<code>/{command_name} FIRST LAST</code>\n\n"
                    "Example:\n"
                    f"<code>/{command_name} 100 120</code>\n\n"
                    "Or use Telegram links:\n"
                    f"<code>/{command_name} "
                    "https://t.me/c/1234567890/100 "
                    "https://t.me/c/1234567890/120</code>"
                ),
                parse_mode=enums.ParseMode.HTML
            )

            return

        first_ref = (
            parse_message_reference(
                command_parts[1]
            )
        )

        last_ref = (
            parse_message_reference(
                command_parts[2]
            )
        )

        if not first_ref or not last_ref:

            await message.reply_text(
                "❌ <b>Invalid message references.</b>",
                parse_mode=enums.ParseMode.HTML
            )

            return

        first_chat, first_id = first_ref
        last_chat, last_id = last_ref

        if str(first_chat) != str(
            DATABASE_CHANNEL_ID
        ):

            await message.reply_text(
                (
                    "❌ <b>First message is not "
                    "from the Database channel.</b>"
                ),
                parse_mode=enums.ParseMode.HTML
            )

            return

        if str(last_chat) != str(
            DATABASE_CHANNEL_ID
        ):

            await message.reply_text(
                (
                    "❌ <b>Last message is not "
                    "from the Database channel.</b>"
                ),
                parse_mode=enums.ParseMode.HTML
            )

            return

    # ========================================================
    # VERIFY IDS
    # ========================================================

    if first_id > last_id:

        first_id, last_id = (
            last_id,
            first_id
        )

    total = (
        last_id
        - first_id
        + 1
    )

    if total > MAX_BATCH_FILES:

        await message.reply_text(
            (
                "❌ <b>Batch too large.</b>\n\n"
                f"Maximum allowed: "
                f"<b>{MAX_BATCH_FILES}</b> files.\n"
                f"Requested: <b>{total}</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # VERIFY FIRST MESSAGE
    # ========================================================

    first_message = (
        await get_database_message(
            client,
            first_id
        )
    )

    if not first_message:

        await message.reply_text(
            (
                "❌ <b>First Database message "
                "was not found.</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # VERIFY LAST MESSAGE
    # ========================================================

    last_message = (
        await get_database_message(
            client,
            last_id
        )
    )

    if not last_message:

        await message.reply_text(
            (
                "❌ <b>Last Database message "
                "was not found.</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # CREATE TOKEN
    # ========================================================

    token = make_batch_token(
        first_id,
        last_id,
        protected=protected
    )

    link = await make_start_link(
        client,
        token
    )

    if not link:

        await message.reply_text(
            "❌ <b>Bot username is not available.</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # ========================================================
    # SEND RESULT
    # ========================================================

    batch_type = (
        "Pʀᴏᴛᴇᴄᴛᴇᴅ Bᴀᴛᴄʜ"
        if protected
        else "Nᴏʀᴍᴀʟ Bᴀᴛᴄʜ"
    )

    await message.reply_text(
        (
            "🔗 <b>Pᴇʀᴍᴀɴᴇɴᴛ Bᴀᴛᴄʜ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
            f"📦 <b>Tʏᴘᴇ:</b> {batch_type}\n"
            f"📁 <b>Fɪʟᴇs:</b> {total}\n"
            f"🔢 <b>Rᴀɴɢᴇ:</b> "
            f"{first_id} - {last_id}\n\n"
            f"🔗 <b><a href=\"{link}\">Oᴘᴇɴ Bᴀᴛᴄʜ Lɪɴᴋ</a></b>\n\n"
            f"<b>Powered By: "
            f"<a href=\"{UPDATES_URL}\">Aᴇʀᴏ Uɴɪᴛʏ</a></b>"
        ),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=False,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Uᴘᴅᴀᴛᴇs •",
                        url=UPDATES_URL
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

# ============================================================
# /BATCH
# OWNER ONLY
# ============================================================

async def batch_handler(
    client,
    message
):

    await generate_batch_link(
        client=client,
        message=message,
        protected=False
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# /PBATCH
# OWNER ONLY
# ============================================================

async def pbatch_handler(
    client,
    message
):

    await generate_batch_link(
        client=client,
        message=message,
        protected=True
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_permanent_link_handlers(app):

    # --------------------------------------------------------
    # /plink - OWNER ONLY - PRIVATE PM
    # --------------------------------------------------------

    app.on_message(
        filters.command("plink")
        & filters.private
    )(plink_handler)

    # --------------------------------------------------------
    # /batch - OWNER ONLY - PRIVATE PM
    # --------------------------------------------------------

    app.on_message(
        filters.command("batch")
        & filters.private
    )(batch_handler)

    # --------------------------------------------------------
    # /pbatch - OWNER ONLY - PRIVATE PM
    # --------------------------------------------------------

    app.on_message(
        filters.command("pbatch")
        & filters.private
    )(pbatch_handler)

    logger.info(
        "Permanent link handlers registered - OWNER ONLY"
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #