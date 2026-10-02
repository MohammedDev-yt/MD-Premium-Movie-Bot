# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import os
import asyncio
import logging

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram.errors import MessageNotModified
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

from config import (
    FREE_REQUESTS
)

from database import (
    get_user,
    create_user,
    update_user
)

from premium import (
    get_user_plan_text,
    format_plans
)

from utils.buttons import (
    home_buttons,
    premium_buttons,
    account_buttons
)

from handlers.search import (
    handle_file_deep_link,
    handle_sendall_deep_link
)

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

START_IMAGE = os.getenv(
    "START_IMAGE",
    ""
)

UPDATES_URL = os.getenv(
    "UPDATES_URL",
    "https://t.me/Aero_Unity"
)

MOVIES_GROUP_URL = os.getenv(
    "MOVIES_GROUP_URL",
    "https://t.me/+YaRuf7dVB6RlZWJl"
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# START BUTTONS
# ============================================================

def start_buttons(
    bot_username
):

    add_group_url = (
        f"https://t.me/{bot_username}"
        f"?startgroup=true"
    )

    return InlineKeyboardMarkup(
        [

            [

                InlineKeyboardButton(
                    "• ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ •",
                    url=add_group_url
                )
            ],

            [

                InlineKeyboardButton(
                    "• ғᴇᴀᴛᴜʀᴇs •",
                    callback_data="features"
                ),

                InlineKeyboardButton(
                    "• ʜᴇʟᴘ •",
                    callback_data="help"
                )
            ],

            [

                InlineKeyboardButton(
                    "• ᴍᴏᴠɪᴇs ɢʀᴏᴜᴘ •",
                    url=MOVIES_GROUP_URL
                )
            ],

            [

                InlineKeyboardButton(
                    "• ᴀʙᴏᴜᴛ •",
                    callback_data="start_about"
                ),

                InlineKeyboardButton(
                    "• ᴜᴘᴅᴀᴛᴇs •",
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
# START TEXT
# ============================================================

def build_start_text(
    first_name,
    remaining,
    user_id
):

    first_name = (
        first_name
        or "User"
    )

    from html import escape

    clickable_name = (
        f'<a href="tg://user?id={user_id}">'
        f'{escape(first_name.upper())}'
        f'</a>'
    )

    return (

        f"👋 <b>Hey {clickable_name} "
        f"Mʏ Nᴀᴍᴇ Is Pʀᴇᴍɪᴜᴍ Mᴏᴠɪᴇ Bᴏᴛ</b>\n\n"

        "<b>I ᴀᴍ A Pᴏᴡᴇʀғᴜʟ Mᴏᴠɪᴇ Sᴇᴀʀᴄʜ Bᴏᴛ.</b> "

        "<b>ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ</b> "

        "<b>ɪ ᴡɪʟʟ ɢɪᴠᴇ ᴍᴏᴠɪᴇs ᴏʀ sᴇʀɪᴇs "
        "ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘᴍ !! 😍</b>\n\n"

        '<b>Mᴀɪɴᴛᴀɪɴᴇᴅ ʙʏ: '
        '<a href="tg://user?id=7284759394">'
        'ᴍᴏʜᴀᴍᴍᴇᴅ'
        '</a></b>'
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# ENSURE USER
# ============================================================

async def ensure_start_user(
    message
):

    user_id = message.from_user.id

    first_name = (
        message.from_user.first_name
        or "User"
    )

    username = (
        message.from_user.username
        or ""
    )

    user = await get_user(
        user_id
    )

    if not user:

        user = await create_user(

            user_id=user_id,

            first_name=first_name,

            username=username
        )

    else:

        await update_user(

            user_id=user_id,

            first_name=first_name,

            username=username
        )

        user = await get_user(
            user_id
        )

    return user

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER
# ============================================================

def register_start_handlers(
    app
):

    # ========================================================
    # START
    # ========================================================

    @app.on_message(
        filters.private
        & filters.command("start")
    )
    async def start_handler(
        client,
        message
    ):

        user_id = (
            message.from_user.id
        )

        logger.info(
            "START RECEIVED from %s",
            user_id
        )

        # ----------------------------------------------------
        # PAYLOAD
        # ----------------------------------------------------

        payload = ""

        if (
            message.command
            and len(message.command) > 1
        ):

            payload = (
                message.command[1]
                .strip()
            )

        # ----------------------------------------------------
        # PERMANENT LINK
        # ----------------------------------------------------


        if (
            payload.startswith("pl_")
            or payload.startswith("pb_")
        ):

            from handlers.permanent_links import (
                handle_permanent_link
            )

            await handle_permanent_link(

                client=client,

                message=message,

                token=payload,

                user_id=user_id
            )

            return


        # ----------------------------------------------------
        # FILE DEEP LINK
        # ----------------------------------------------------

        if payload.startswith(
            "file_"
        ):

            try:

                message_id = int(
                    payload.split(
                        "_",
                        1
                    )[1]
                )

            except (
                ValueError,
                IndexError
            ):

                await message.reply_text(
                    "❌ <b>Invalid file link.</b>"
                )

                return

            await handle_file_deep_link(

                client=client,

                message=message,

                message_id=message_id,

                user_id=user_id
            )

            return

        # ----------------------------------------------------
        # SEND ALL DEEP LINK
        # ----------------------------------------------------

        if payload.startswith(
            "sendall_"
        ):

            try:

                parts = payload.split(
                    "_"
                )

                if len(parts) != 3:

                    raise ValueError

                session_id = parts[1]

                page = int(
                    parts[2]
                )

            except (
                ValueError,
                IndexError
            ):

                await message.reply_text(
                    "❌ <b>Invalid Send All link.</b>"
                )

                return

            await handle_sendall_deep_link(

                client=client,

                message=message,

                session_id=session_id,

                page=page,

                user_id=user_id
            )

            return

        # ----------------------------------------------------
        # NORMAL START
        # ----------------------------------------------------

        user = await ensure_start_user(
            message
        )

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        try:

            animation = await client.send_message(
                chat_id=user_id,
                text="⚡️"
            )

            await asyncio.sleep(
                0.6
            )

            await animation.edit_text(
                "卍解 Bᴀɴᴋᴀɪ"
            )

            await asyncio.sleep(
                0.6
            )

            await animation.edit_text(
                "Tᴇɴsᴀ Zᴀɴɢᴇᴛsᴜ"
            )

            await asyncio.sleep(
                0.6
            )

            await animation.edit_text(
                "Iᴄʜɪɢᴏ Kᴜʀᴏsᴀᴋɪ..."
            )

            await asyncio.sleep(
                0.6
            )

            await animation.delete()

        except Exception as e:

            logger.warning(
                "START ANIMATION ERROR: %s",
                e
            )

        # ----------------------------------------------------
        # REQUESTS
        # ----------------------------------------------------

        remaining = user.get(
            "remaining_requests",
            FREE_REQUESTS
        )

        # ----------------------------------------------------
        # BOT USERNAME
        # ----------------------------------------------------

        me = await client.get_me()

        bot_username = (
            me.username
            or ""
        )

        # ----------------------------------------------------
        # START SCREEN
        # ----------------------------------------------------

        text = build_start_text(
            first_name=(
                message.from_user.first_name
                or "User"
            ),
            remaining=remaining,
            user_id=user_id
        )

        keyboard = start_buttons(
            bot_username
        )

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        if START_IMAGE:

            try:

                sent = await message.reply_photo(
                    photo=START_IMAGE,
                    caption=text,
                    reply_markup=keyboard
                )
                return

            except Exception as e:

                logger.warning(
                    "START IMAGE SEND FAILED: %s",
                    e
                )

        # ----------------------------------------------------
        # TEXT
        # ----------------------------------------------------

        await message.reply_text(
            text,
            reply_markup=keyboard
        )
    
    # ========================================================
    # FEATURES
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^features$"
        )
    )
    async def features_callback(
        client,
        callback
    ):

        text = (
            " <b>Fᴇᴀᴛᴜʀᴇs</b>\n\n"

            "<b>›› Sᴇʟᴇᴄᴛ A Fᴇᴀᴛᴜʀᴇ Bᴇʟᴏᴡ "
            "Tᴏ Sᴇᴇ Hᴏᴡ Tᴏ Uѕᴇ Iᴛ.</b>"
        )

        buttons = InlineKeyboardMarkup(
            [

                [
                    InlineKeyboardButton(
                        "• Sʏsᴛᴇᴍ •",
                        callback_data="feature_system"
                    ),

                    InlineKeyboardButton(
                        "• Sᴛᴀᴛs •",
                        callback_data="feature_stats"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "• Sʜᴀʀᴇ •",
                        callback_data="feature_share"
                    ),

                    InlineKeyboardButton(
                        "• Tᴇʟᴇɢʀᴀᴘʜ •",
                        callback_data="feature_telegraph"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "• Fᴏɴᴛ •",
                        callback_data="feature_font"
                    )
                ],

                [
                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            if callback.message.photo:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            else:

                await callback.message.edit_text(
                    text,
                    reply_markup=buttons
                )

        except MessageNotModified:
            pass

        except Exception as e:

            logger.warning(
                "FEATURES EDIT ERROR: %s",
                e
            )

        await callback.answer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # SYSTEM HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^feature_system$"
        )
    )
    async def feature_system_callback(
        client,
        callback
    ):

        text = (
            "<b>Sʏsᴛᴇᴍ</b>\n\n"

            "<b>Sʜᴏᴡs Tʜᴇ Bᴏᴛ's Sʏsᴛᴇᴍ "
            "Aɴᴅ Sᴇʀᴠᴇʀ Iɴғᴏʀᴍᴀᴛɪᴏɴ.</b>\n\n"

            "📌 <b>Hᴏᴡ Tᴏ Uѕᴇ:</b>\n\n"

            "Sᴇɴᴅ:\n"
            "<code>/system</code>\n\n"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Fᴇᴀᴛᴜʀᴇs •",
                        callback_data="features"
                    ),

                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=buttons
            )

        except Exception:

            try:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:

                logger.warning(
                    "SYSTEM HELP ERROR: %s",
                    e
                )

        await callback.answer()


    # ========================================================
    # STATS HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
             r"^feature_stats$"
        )
    )
    async def feature_stats_callback(
        client,
        callback
    ):

        text = (
            "📊 <b>Sᴛᴀᴛs</b>\n\n"

            "<b>Sʜᴏᴡs Tʜᴇ Bᴏᴛ's "
            "Cᴜʀʀᴇɴᴛ Sᴛᴀᴛɪsᴛɪᴄs.</b>\n\n"

            "📌 <b>Hᴏᴡ Tᴏ Uѕᴇ:</b>\n\n"

            "Sᴇɴᴅ:\n"
            "<code>/stats</code>\n\n"   
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Fᴇᴀᴛᴜʀᴇs •",
                        callback_data="features"
                    ),

                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=buttons
            )

        except Exception:

            try:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:

                logger.warning(
                    "STATS HELP ERROR: %s",
                    e
                )

        await callback.answer()

    # ========================================================
    # SHARE HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^feature_share$"
        )
    )
    async def feature_share_callback(
        client,
        callback
    ):

        text = (
            "<b>Sʜᴀʀᴇ</b>\n\n"

            "<b>Sʜᴀʀᴇ A Tᴇxᴛ Mᴇssᴀɢᴇ "
            "Tʜʀᴏᴜɢʜ Tʜᴇ Bᴏᴛ.</b>\n\n"

            "📌 <b>Hᴏᴡ Tᴏ Uѕᴇ:</b>\n\n"

            "<code>/share Your Text</code>\n\n"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Fᴇᴀᴛᴜʀᴇs •",
                        callback_data="features"
                    ),

                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=buttons
            )

        except Exception:

            try:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:

                logger.warning(
                    "SHARE HELP ERROR: %s",
                    e
                )

        await callback.answer()


    # ========================================================
    # TELEGRAPH HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^feature_telegraph$"
        )
    )
    async def feature_telegraph_callback(
        client,
        callback
    ):

        text = (
            " <b>Tᴇʟᴇɢʀᴀᴘʜ</b>\n\n"

            "<b>Cᴏɴᴠᴇʀ Aɴ Iᴍᴀɢᴇ Iɴᴛᴏ A "
            "Tᴇʟᴇɢʀᴀᴘʜ Lɪɴᴋ.</b>\n\n"

            "📌 <b>Hᴏᴡ Tᴏ Uѕᴇ:</b>\n\n"

            "1️⃣ Sᴇɴᴅ Aɴ Iᴍᴀɢᴇ Tᴏ Tʜᴇ Bᴏᴛ.\n\n"

            "2️⃣ Rᴇᴘʟʏ Tᴏ Tʜᴇ Iᴍᴀɢᴇ Wɪᴛʜ:\n"
            "<code>/telegraph</code>\n\n"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Fᴇᴀᴛᴜʀᴇs •",
                        callback_data="features"
                    ),

                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=buttons
            )

        except Exception:

            try:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:

                logger.warning(
                    "TELEGRAPH HELP ERROR: %s",
                    e
                )

        await callback.answer()

    # ========================================================
    # FONT HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^feature_font$"
        )
    )
    async def feature_font_callback(
        client,
        callback
    ):

        text = (
            " <b>Fᴏɴᴛ</b>\n\n"

            "<b>Cʜᴀɴɢᴇ Yᴏᴜʀ Tᴇxᴛ Iɴᴛᴏ "
            "Dɪғғᴇʀᴇɴᴛ Fᴏɴᴛ Sᴛʏʟᴇs.</b>\n\n"

            "📌 <b>Hᴏᴡ Tᴏ Uѕᴇ:</b>\n\n"

            "<code>/font Your Text</code>\n\n"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Fᴇᴀᴛᴜʀᴇs •",
                        callback_data="features"
                    ),

                    InlineKeyboardButton(
                        "• Hᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=buttons
            )

        except Exception:

            try:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            except Exception as e:

                logger.warning(
                    "FONT HELP ERROR: %s",
                    e
                )

        await callback.answer()



    # ========================================================
    # ABOUT
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^start_about$"
        )
    )
    async def start_about_callback(
        client,
        callback
    ):

        text = (

            "<b>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</b>\n\n"

            "• <b>Pʀᴏɢʀᴀᴍᴇʀ: "
            "<a href=\"https://t.me/Mr_Mohammed_29\">"
            "ᴍᴏʜᴀᴍᴍᴇᴅ</a></b>\n"

            "• <b>ꜰᴏᴜɴᴅᴇʀ ᴏꜰ: "
            "<a href=\"https://t.me/Aero_Unity\">"
            "ᴀᴇʀᴏ ᴜɴɪᴛʏ</a></b>\n"

            "• <b>Lɪʙʀᴀʀʏ: Pyʀᴏɢʀᴀᴍ 2.0</b>\n"

            "• <b>Lᴀɴɢᴜᴀɢᴇ: Pʏᴛʜᴏɴ 𝟹</b>\n"

            "• <b>ᴅᴀᴛᴀʙᴀsᴇ: ᴍᴏɴɢᴏ ᴅʙ</b>\n"

            "• <b>ᴄʜᴀɴɴᴇʟ: "
            "<a href=\"https://t.me/Aero_Unity\">"
            "ᴀᴇʀᴏ ᴜɴɪᴛʏ</a></b>\n"

            "<b>Bᴜɪʟᴅ Sᴛᴀᴛᴜs: ᴠ3 [sᴛᴀʙʟᴇ]</b>"
        )

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• ʜᴏᴍᴇ •",
                        callback_data="start_back"
                    )
                ]
            ]
        )

        try:

            if callback.message.photo:

                await callback.message.edit_caption(
                    caption=text,
                    reply_markup=buttons
                )

            else:

                await callback.message.edit_text(
                    text,
                    reply_markup=buttons
                )

        except Exception as e:

            logger.warning(
                "ABOUT EDIT ERROR: %s",
                e
            )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # HOME
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^home$"
        )
    )
    async def home_callback(
        client,
        callback
    ):

        user_id = callback.from_user.id

        user = await get_user(
            user_id
        )

        if not user:

            user = await create_user(

                user_id=user_id,

                first_name=(
                    callback.from_user.first_name
                    or "User"
                ),

                username=(
                    callback.from_user.username
                    or ""
                )
            )

        remaining = user.get(
            "remaining_requests",
            FREE_REQUESTS
        )

        text = (

            "<b>Pʀᴇᴍɪᴜᴍ Mᴏᴠɪᴇ Bᴏᴛ</b>\n\n"

            f"🎟 ғʀᴇᴇ ʀᴇǫᴜᴇsᴛs ʀᴇᴍᴀɪɴɪɴɢ: "
            f"<b>{remaining}</b>"
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=home_buttons()
            )

        except Exception:

            pass

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # ACCOUNT
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^my_account$"
        )
    )
    async def account_callback(
        client,
        callback
    ):

        user_id = callback.from_user.id

        user = await get_user(
            user_id
        )

        if not user:

            user = await create_user(

                user_id=user_id,

                first_name=(
                    callback.from_user.first_name
                    or "User"
                ),

                username=(
                    callback.from_user.username
                    or ""
                )
            )

        text = get_user_plan_text(
            user
        )

        await callback.message.edit_text(
            text,
            reply_markup=account_buttons()
        )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # PREMIUM
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^premium_plans$"
        )  
    )
    async def premium_plans_callback(
        client,
        callback
    ):

        try:

            await callback.message.edit_text(
                format_plans(),
                reply_markup=premium_buttons()
            )

        except MessageNotModified:

            pass

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^help$"
        )
    )
    async def help_callback(
        client,
        callback
    ):

        text = (

            "📚 <b>Hᴇʟᴘ & Mᴏᴠɪᴇ Rᴜʟᴇs</b>\n\n"

            "🎬 <b>Hᴏᴡ Tᴏ Sᴇᴀʀᴄʜ:</b>\n\n"

            "➤ Sᴇɴᴅ Tʜᴇ Mᴏᴠɪᴇ Oʀ Sᴇʀɪᴇs Nᴀᴍᴇ.\n\n"

            "➤ Tʜᴇ Bᴏᴛ Wɪʟʟ Sᴇᴀʀᴄʜ Mʏ Dᴀᴛᴀʙᴀsᴇ.\n\n"

            "➤ Sᴇʟᴇᴄᴛ Tʜᴇ Rᴇǫᴜɪʀᴇᴅ Fɪʟᴇ.\n\n"

            "⚠️ <b>Mᴏᴠɪᴇ Sᴇᴀʀᴄʜ Rᴜʟᴇs:</b>\n\n"

            "• Dᴏ Nᴏᴛ Sᴇɴᴅ Pʜᴏᴛᴏs.\n"
            "• Dᴏ Nᴏᴛ Sᴇɴᴅ Vɪᴅᴇᴏs.\n"
            "• Dᴏ Nᴏᴛ Sᴇɴᴅ Dᴏᴄᴜᴍᴇɴᴛs.\n"
            "• Dᴏ Nᴏᴛ Sᴇɴᴅ Uʀʟs.\n\n"

            "🔎 <b>Sᴇᴀʀᴄ Exᴀᴍᴘʟᴇ:</b>\n"
            "<code>Avengers Endgame</code>\n\n"

            f"🆓 Fʀᴇᴇ Rᴇǫᴜᴇsᴛs: "
            f"<b>{FREE_REQUESTS}</b>\n\n"

            "<b> Aᴄᴛɪᴠᴀᴛᴇ Pʀᴇᴍɪᴜᴍ Aғᴛᴇʀ Yᴏᴜʀ "
            "Fʀᴇᴇ Rᴇǫᴜᴇsᴛs Aʀᴇ Fɪɴɪsʜᴇᴅ.</b>"
        )

        await callback.message.edit_text(

            text,

            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• ʜᴏᴍᴇ •",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # SEARCH HELP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^search_help$"
        )
    )
    async def search_help_callback(
        client,
        callback
    ):

        text = (

            "🔎 <b>Sᴇᴀʀᴄ Mᴏᴠɪᴇs</b>\n\n"

            "Sᴇɴᴅ Tʜᴇ Nᴀᴍᴇ Oғ Tʜᴇ Mᴏᴠɪᴇ, "
            "Sᴇʀɪᴇs, Oʀ Aɴɪᴍᴇ.\n\n"

            "<b>Example:</b>\n"
            "<code>Avengers Endgame</code>"
        )

        await callback.message.edit_text(

            text,

            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• ʜᴏᴍᴇ •",
                            callback_data="home"
                        )
                    ]
                ]
            )
        )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # START BACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^start_back$"
        )
    )
    async def start_back_callback(
        client,
        callback
    ):

        user_id = callback.from_user.id

        first_name = (
            callback.from_user.first_name
            or "User"
        )

        username = (
            callback.from_user.username
            or ""
        )

        user = await get_user(
            user_id
        )

        if not user:

            user = await create_user(

                user_id=user_id,

                first_name=first_name,

                username=username
            )

        else:

            await update_user(

                user_id=user_id,

                first_name=first_name,

                username=username
            )

            user = await get_user(
                user_id
            )

        remaining = user.get(
            "remaining_requests",
            FREE_REQUESTS
        )

        me = await client.get_me()

        bot_username = (
            me.username
            or ""
        )

        text = build_start_text(
            first_name,
            remaining,
            user_id
        )

        keyboard = start_buttons(
            bot_username
        )

        await callback.answer()

        try:

            await callback.message.delete()

        except Exception:

            pass

        if START_IMAGE:

            try:
                await client.send_photo(
                    chat_id=user_id,
                    photo=START_IMAGE,
                    caption=text,
                    reply_markup=keyboard
                )

                return

            except Exception as e:
                logger.warning(
                    "START BACK IMAGE ERROR: %s",
                    e
                )

        await client.send_message(  
            chat_id=user_id, 
            text=text,
            reply_markup=keyboard
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # CLOSE
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^close$"
        )
    )
    async def close_callback(
        client,
        callback
    ):

        await callback.answer()

        try:

            await callback.message.delete()

        except Exception as e:

            logger.warning(
                "CLOSE MESSAGE DELETE ERROR: %s",
                e
            )
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # PREMIUM BACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^premium$"
        )
    )
    async def premium_callback(
        client,
        callback
    ):

        await callback.answer()

        await callback.message.edit_text(
            format_plans(),
            reply_markup=premium_buttons()
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #