
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #

import asyncio
import logging
import re
from html import escape

from pyrogram import filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import DATABASE_CHANNEL_ID, OWNER_ID
from handlers.fsub import check_all_fsubs, send_fsub_message

logger = logging.getLogger(__name__)

MAX_BATCH_FILES = 50
DELETE_AFTER = 300
UPDATES_URL = "https://t.me/Aero_Unity"


# ============================================================
# OWNER CHECK
# ============================================================

def is_owner(message):
    try:
        return (
            message.from_user is not None
            and int(message.from_user.id) == int(OWNER_ID)
        )
    except (TypeError, ValueError):
        return False


async def owner_required(message):
    if not await asyncio.sleep(0) and not is_owner(message):
        await message.reply_text(
            "❌ <b>Only the Owner can use this command.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return False
    return True


# ============================================================
# DELETE MESSAGES AFTER FIVE MINUTES
# ============================================================

async def delete_after_5_minutes(client, chat_id, message_id):
    try:
        await asyncio.sleep(DELETE_AFTER)
        await client.delete_messages(chat_id, message_id)
        logger.info(
            "MESSAGE DELETED | chat=%s | message=%s",
            chat_id,
            message_id
        )
    except asyncio.CancelledError:
        raise
    except Exception as e:
        logger.warning(
            "Failed to delete message | chat=%s | message=%s | error=%s",
            chat_id,
            message_id,
            e
        )


def schedule_deletion(client, chat_id, message_id):
    asyncio.create_task(
        delete_after_5_minutes(client, chat_id, message_id)
    )


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
        return int("-100" + match.group(1)), int(match.group(2))

    match = re.search(
        r"(?:https?://)?t\.me/([A-Za-z0-9_]+)/(\d+)",
        text
    )

    if match:
        return match.group(1), int(match.group(2))

    return None


def parse_message_reference(value):
    if not value:
        return None

    value = value.strip()

    if value.isdigit():
        return DATABASE_CHANNEL_ID, int(value)

    return get_message_id_from_link(value)


def make_single_token(message_id):
    return f"pl_{message_id}"


def make_batch_token(first_id, last_id, protected=False):
    prefix = "pb_" if protected else "ba_"
    return f"{prefix}{first_id}_{last_id}"


async def make_start_link(client, token):
    try:
        me = await client.get_me()
        if not me.username:
            return None
        return f"https://t.me/{me.username}?start={token}"
    except Exception as e:
        logger.error("Failed to create start link: %s", e)
        return None


# ============================================================
# FORWARDED MESSAGE ORIGINAL SOURCE
# ============================================================

def get_original_message_reference(message):
    original_chat_id = None
    original_message_id = None

    try:
        forward_origin = getattr(message, "forward_origin", None)

        if forward_origin:
            original_message_id = getattr(
                forward_origin, "message_id", None
            )
            origin_chat = getattr(forward_origin, "chat", None)

            if origin_chat:
                original_chat_id = getattr(origin_chat, "id", None)
    except Exception as e:
        logger.warning("forward_origin read failed: %s", e)

    if not original_message_id:
        original_message_id = getattr(
            message, "forward_from_message_id", None
        )

    if not original_chat_id:
        forward_chat = getattr(message, "forward_from_chat", None)
        if forward_chat:
            original_chat_id = getattr(forward_chat, "id", None)

    if not original_message_id:
        return None

    return original_chat_id, int(original_message_id)


# ============================================================
# DATABASE MESSAGE
# ============================================================

async def get_database_message(client, message_id):
    try:
        message = await client.get_messages(
            DATABASE_CHANNEL_ID,
            int(message_id)
        )

        if not message or getattr(message, "empty", False):
            return None

        return message

    except Exception as e:
        logger.error(
            "Failed to get database message %s: %s",
            message_id,
            e
        )
        return None


# ============================================================
# MEDIA CHECK
# ============================================================

def has_supported_media(message):
    if not message:
        return False

    return any((
        message.document,
        message.video,
        message.audio,
        message.animation,
        message.voice,
        message.photo
    ))


# ============================================================
# WARNING TEXT
# ============================================================

def build_delete_warning_text(batch=False):
    if batch:
        file_text = "Fɪʟᴇs"
        forward_text = "Tʜᴇᴍ"
        episode_text = "Eᴘɪѕᴏᴅᴇs"
    else:
        file_text = "Fɪʟᴇ"
        forward_text = "Iᴛ"
        episode_text = "Eᴘɪѕᴏᴅᴇ"

    return (
        "<b>⌛ Dᴜᴇ Tᴏ Cᴏᴘʏʀɪɢʜᴛ Iѕѕᴜᴇѕ...</b>\n\n"
        f"» Yᴏᴜʀ {file_text} Wɪʟʟ Bᴇ Dᴇʟᴇᴛᴇᴅ Wɪᴛʜɪɴ 5 Mɪɴ.\n"
        f"» Pʟᴇᴀѕᴇ Fᴏʀᴡᴀʀᴅ {forward_text} Tᴏ Aɴᴏᴛʜᴇʀ "
        "Cʜᴀᴛ Oʀ Sᴀᴠᴇ Iᴛ Tᴏ Sᴀᴠᴇᴅ Mᴇѕѕᴀɢᴇѕ "
        "Fᴏʀ Fᴜᴛᴜʀᴇ Aᴠᴀɪʟᴀʙɪʟɪᴛʏ.\n\n"
        f"» Nᴏᴛᴇ: Uѕᴇ VLC Pʟᴀʏᴇʀ Oʀ MX Pʟᴀʏᴇʀ "
        f"Tᴏ Wᴀᴛᴄʜ Tʜᴇ {episode_text} Wɪᴛʜ A Gᴏᴏᴅ "
        "Exᴘᴇʀɪᴇɴᴄᴇ."
    )


# ============================================================
# FILE CAPTION
# ============================================================

def build_file_caption(database_message, batch=False):
    original_caption = (
        getattr(database_message, "caption", None) or ""
    ).strip()

    if original_caption:
        title = escape(original_caption[:900])
    else:
        title = "📁 Yᴏᴜʀ Rᴇǫᴜᴇsᴛᴇᴅ Fɪʟᴇ"

    return f'<b><a href="{UPDATES_URL}">{title}</a></b>'


# ============================================================
# FILE KEYBOARD
# ============================================================

def build_file_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "• Uᴘᴅᴀᴛᴇs •",
                url=UPDATES_URL
            )
        ]
    ])


# ============================================================
# SEND WARNING AS A REPLY TO A FILE
# ============================================================

async def send_warning_for_file(client, user_id, file_message, batch=False):
    if not file_message:
        return None

    try:
        warning = await client.send_message(
            chat_id=user_id,
            text=build_delete_warning_text(batch=batch),
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=file_message.id
        )

        schedule_deletion(client, user_id, warning.id)
        return warning

    except Exception as e:
        logger.warning(
            "Failed to send warning | user=%s | error=%s",
            user_id,
            e
        )
        return None


# ============================================================
# SEND ONE PERMANENT FILE
# ============================================================

async def send_permanent_file(
    client,
    user_id,
    message_id,
    protected=False,
    batch=False,
    send_warning=True
):
    database_message = await get_database_message(
        client, message_id
    )

    if not database_message or not has_supported_media(database_message):
        return None

    try:
        sent_message = await client.copy_message(
            chat_id=user_id,
            from_chat_id=DATABASE_CHANNEL_ID,
            message_id=database_message.id,
            caption=build_file_caption(database_message, batch=batch),
            parse_mode=enums.ParseMode.HTML,
            reply_markup=build_file_keyboard(),
            protect_content=protected
        )

        if not sent_message:
            return None

        schedule_deletion(client, user_id, sent_message.id)

        if send_warning:
            await send_warning_for_file(
                client,
                user_id,
                sent_message,
                batch=batch
            )

        logger.info(
            "PERMANENT FILE SENT | user=%s | message_id=%s | protected=%s",
            user_id,
            message_id,
            protected
        )

        return sent_message

    except Exception as e:
        logger.error(
            "PERMANENT FILE SEND ERROR | user=%s | message_id=%s | error=%s",
            user_id,
            message_id,
            e
        )
        return None


# ============================================================
# SEND BATCH: FILES FIRST, ONE WARNING ON LAST FILE
# ============================================================

async def send_permanent_batch(
    client,
    user_id,
    first_id,
    last_id,
    protected=False
):
    if first_id > last_id:
        first_id, last_id = last_id, first_id

    if last_id - first_id + 1 > MAX_BATCH_FILES:
        return 0, True

    sent_count = 0
    last_sent_message = None

    for message_id in range(first_id, last_id + 1):
        database_message = await get_database_message(
            client, message_id
        )

        if not database_message or not has_supported_media(database_message):
            continue

        sent_message = await send_permanent_file(
            client=client,
            user_id=user_id,
            message_id=message_id,
            protected=protected,
            batch=True,
            send_warning=False
        )

        if sent_message:
            sent_count += 1
            last_sent_message = sent_message

    # Send only one warning, as a reply to the last successfully sent file.
    if last_sent_message:
        await send_warning_for_file(
            client,
            user_id,
            last_sent_message,
            batch=True
        )

    return sent_count, False


# ============================================================
# HANDLE PERMANENT LINK
# ============================================================

async def handle_permanent_link(client, message, token, user_id=None):
    if user_id is None:
        if not message.from_user:
            return
        user_id = message.from_user.id

    if not token:
        return

    token = token.strip()

    # FORCE-SUBSCRIPTION CHECK
    try:
        not_joined = await check_all_fsubs(client, user_id)

        if not_joined:
            await send_fsub_message(
                client,
                message,
                not_joined,
                deep_link=token
            )
            return
    except Exception as e:
        logger.error("Force-sub check failed: %s", e)
        return

    # SINGLE FILE
    if token.startswith("pl_"):
        raw_id = token[3:]

        if not raw_id.isdigit():
            await client.send_message(
                user_id,
                "❌ <b>Invalid permanent link.</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return

        sent_message = await send_permanent_file(
            client,
            user_id,
            int(raw_id),
            protected=True,
            batch=False,
            send_warning=True
        )

        if not sent_message:
            await client.send_message(
                user_id,
                "❌ <b>File not found or unavailable.</b>",
                parse_mode=enums.ParseMode.HTML
            )
        return

    # NORMAL / PROTECTED BATCH
    if token.startswith(("ba_", "pb_")):
        protected = token.startswith("pb_")
        raw_range = token[3:].split("_")

        if len(raw_range) != 2 or not all(
            value.isdigit() for value in raw_range
        ):
            await client.send_message(
                user_id,
                "❌ <b>Invalid batch link.</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return

        first_id, last_id = map(int, raw_range)

        sent_count, too_many = await send_permanent_batch(
            client,
            user_id,
            first_id,
            last_id,
            protected=protected
        )

        if too_many:
            await client.send_message(
                user_id,
                (
                    "❌ <b>Batch too large.</b>\n\n"
                    f"Maximum allowed: <b>{MAX_BATCH_FILES}</b> files."
                ),
                parse_mode=enums.ParseMode.HTML
            )
        elif sent_count == 0:
            await client.send_message(
                user_id,
                "❌ <b>No files were found in this batch.</b>",
                parse_mode=enums.ParseMode.HTML
            )
        return

    await client.send_message(
        user_id,
        "❌ <b>Invalid or expired permanent link.</b>",
        parse_mode=enums.ParseMode.HTML
    )


# ============================================================
# /PLINK - OWNER ONLY
# ============================================================

async def plink_handler(client, message):
    if not await owner_required(message):
        return

    if not message.reply_to_message:
        await message.reply_text(
            "❌ <b>Reply to a media message with /plink.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    replied = message.reply_to_message
    original_chat_id = None
    original_message_id = None

    if str(message.chat.id) == str(DATABASE_CHANNEL_ID):
        original_chat_id = DATABASE_CHANNEL_ID
        original_message_id = replied.id
    else:
        reference = get_original_message_reference(replied)
        if reference:
            original_chat_id, original_message_id = reference

    if not original_message_id:
        await message.reply_text(
            (
                "❌ <b>Could not find the original Database message.</b>\n\n"
                "Forward a file from the Database channel and reply to it "
                "with <code>/plink</code>."
            ),
            parse_mode=enums.ParseMode.HTML
        )
        return

    if str(original_chat_id) != str(DATABASE_CHANNEL_ID):
        await message.reply_text(
            "❌ <b>This file is not from the Database channel.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    database_message = await get_database_message(
        client, original_message_id
    )

    if not database_message or not has_supported_media(database_message):
        await message.reply_text(
            "❌ <b>Database media was not found or is unsupported.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    link = await make_start_link(
        client,
        make_single_token(original_message_id)
    )

    if not link:
        await message.reply_text(
            "❌ <b>Bot username is not available.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    await message.reply_text(
        (
            "🔗 <b>Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
            f'🔗 <b><a href="{link}">Oᴘᴇɴ Pᴇʀᴍᴀɴᴇɴᴛ Lɪɴᴋ</a></b>\n\n'
            f'<b>Powered By: <a href="{UPDATES_URL}">Aᴇʀᴏ Uɴɪᴛʏ</a></b>'
        ),
        parse_mode=enums.ParseMode.HTML,
        reply_markup=build_file_keyboard(),
        disable_web_page_preview=True
    )


# ============================================================
# BATCH REFERENCE HELPERS
# ============================================================

def get_batch_reply_reference(replied):
    if not replied:
        return None

    reference = get_original_message_reference(replied)

    if not reference:
        return None

    original_chat_id, original_message_id = reference

    if str(original_chat_id) != str(DATABASE_CHANNEL_ID):
        return None

    return int(original_message_id)


# ============================================================
# GENERATE BATCH LINK
# ============================================================

async def generate_batch_link(client, message, protected=False):
    if not await owner_required(message):
        return

    text = message.text or message.caption or ""
    command_parts = text.split()
    command_name = "pbatch" if protected else "batch"

    first_id = None
    last_id = None

    if message.reply_to_message:
        first_id = get_batch_reply_reference(message.reply_to_message)

        if first_id is not None:
            if len(command_parts) != 2:
                await message.reply_text(
                    (
                        f"❌ <b>Reply to the first Database file and use:</b>\n\n"
                        f"<code>/{command_name} LAST_ID</code>\n\n"
                        f"<b>Example:</b> <code>/{command_name} 120</code>"
                    ),
                    parse_mode=enums.ParseMode.HTML
                )
                return

            last_ref = parse_message_reference(command_parts[1])

            if not last_ref:
                await message.reply_text(
                    "❌ <b>Invalid last message reference.</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                return

            last_chat, last_id = last_ref

            if str(last_chat) != str(DATABASE_CHANNEL_ID):
                await message.reply_text(
                    "❌ <b>The last message must be from the Database channel.</b>",
                    parse_mode=enums.ParseMode.HTML
                )
                return

    if first_id is None:
        if len(command_parts) != 3:
            await message.reply_text(
                (
                    "❌ <b>Invalid format.</b>\n\n"
                    f"Use: <code>/{command_name} FIRST LAST</code>\n\n"
                    f"Example: <code>/{command_name} 100 120</code>"
                ),
                parse_mode=enums.ParseMode.HTML
            )
            return

        first_ref = parse_message_reference(command_parts[1])
        last_ref = parse_message_reference(command_parts[2])

        if not first_ref or not last_ref:
            await message.reply_text(
                "❌ <b>Invalid message references.</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return

        first_chat, first_id = first_ref
        last_chat, last_id = last_ref

        if str(first_chat) != str(DATABASE_CHANNEL_ID):
            await message.reply_text(
                "❌ <b>First message is not from the Database channel.</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return

        if str(last_chat) != str(DATABASE_CHANNEL_ID):
            await message.reply_text(
                "❌ <b>Last message is not from the Database channel.</b>",
                parse_mode=enums.ParseMode.HTML
            )
            return

    first_id = int(first_id)
    last_id = int(last_id)

    if first_id > last_id:
        first_id, last_id = last_id, first_id

    total = last_id - first_id + 1

    if total > MAX_BATCH_FILES:
        await message.reply_text(
            (
                "❌ <b>Batch too large.</b>\n\n"
                f"Maximum allowed: <b>{MAX_BATCH_FILES}</b> files.\n"
                f"Requested: <b>{total}</b>"
            ),
            parse_mode=enums.ParseMode.HTML
        )
        return

    first_message = await get_database_message(client, first_id)
    last_message = await get_database_message(client, last_id)

    if not first_message or not last_message:
        await message.reply_text(
            "❌ <b>First or last Database message was not found.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    token = make_batch_token(first_id, last_id, protected=protected)
    link = await make_start_link(client, token)

    if not link:
        await message.reply_text(
            "❌ <b>Bot username is not available.</b>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    batch_type = "Pʀᴏᴛᴇᴄᴛᴇᴅ Bᴀᴛᴄʜ" if protected else "Nᴏʀᴍᴀʟ Bᴀᴛᴄʜ"

    await message.reply_text(
        (
            "🔗 <b>Pᴇʀᴍᴀɴᴇɴᴛ Bᴀᴛᴄʜ Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
            f"📦 <b>Tʏᴘᴇ:</b> {batch_type}\n"
            f"📁 <b>Mᴀxɪᴍᴜᴍ Rᴀɴɢᴇ:</b> {total}\n"
            f"🔢 <b>Rᴀɴɢᴇ:</b> {first_id} - {last_id}\n\n"
            f'🔗 <b><a href="{link}">Oᴘᴇɴ Bᴀᴛᴄʜ Lɪɴᴋ</a></b>\n\n'
            f'<b>Powered By: <a href="{UPDATES_URL}">Aᴇʀᴏ Uɴɪᴛʏ</a></b>'
        ),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
        reply_markup=build_file_keyboard()
    )


# ============================================================
# COMMAND HANDLERS
# ============================================================

async def batch_handler(client, message):
    await generate_batch_link(client, message, protected=False)


async def pbatch_handler(client, message):
    await generate_batch_link(client, message, protected=True)


# ============================================================
# REGISTER HANDLERS
# ============================================================

def register_permanent_link_handlers(app):
    app.on_message(
        filters.command("plink") & filters.private
    )(plink_handler)

    app.on_message(
        filters.command("batch") & filters.private
    )(batch_handler)

    app.on_message(
        filters.command("pbatch") & filters.private
    )(pbatch_handler)

    logger.info("Permanent link handlers registered - OWNER ONLY")


# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #