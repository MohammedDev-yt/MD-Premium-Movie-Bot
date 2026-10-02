# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import logging
import asyncio
import os
import time
import psutil
import importlib
import config

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from html import escape
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

from pyrogram import filters
from pyrogram.enums import ChatType
from config import OWNER_ID, ADMIN_IDS
from premium import get_plan_by_amount

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from database import (
    get_user,
    get_all_user_ids,
    users_collection,
    count_users,
    count_premium_users,
    count_media,
    count_chats,
    get_stats,
    get_media_storage_stats,
    activate_premium,
    remove_premium,
    get_indexer_state,
    get_trending_searches,
    get_admin,
    get_admins,
    add_admin,
    remove_admin,
    update_admin_info,
    add_warning,
    get_warnings,
    reset_warnings,
    get_all_warnings,
    remove_warning,
    optimize_database
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
    return user_id == OWNER_ID or user_id in ADMIN_IDS


admin_only = filters.create(
    lambda _, __, message: (
        message.from_user is not None
        and is_admin(message.from_user.id)
    )
)

# ============================================================
# LOAD MONGODB ADMINS
# ============================================================

async def load_mongodb_admins():

    try:

        saved_admins = await get_admins()

        ADMIN_IDS.clear()

        for admin in saved_admins:

            user_id = admin.get(
                "user_id"
            )

            if user_id is not None:

                try:
                    ADMIN_IDS.add(
                        int(user_id)
                    )
                except (
                    TypeError,
                    ValueError
                ):
                    pass

        logger.info(
            "Loaded %s admin(s) from MongoDB.",
            len(ADMIN_IDS)
        )

    except Exception as e:

        logger.exception(
            "Failed to load admins from MongoDB: %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER ADMIN HANDLERS
# ============================================================

def register_admin_handlers(app):

    # ========================================================
    # LOAD SAVED ADMINS
    # ========================================================

    try:

        asyncio.get_event_loop().create_task(
            load_mongodb_admins()
        )

    except Exception as e:

        logger.warning(
            "Could not schedule admin loading: %s",
            e
        )

    # ========================================================
    # /alive
    # ========================================================

    @app.on_message(
        filters.command("alive")
    )
    async def alive_handler(
        client,
        message
    ):

        alive_image = os.getenv(
            "ALIVE_IMAGE",
            ""
        )

        text = (
            "Yᴏᴜ ᴀʀᴇ ᴠᴇʀʏ ʟᴜᴄᴋʏ 🤞 "
            "I ᴀᴍ ᴀʟɪᴠᴇ ❤️\n\n"

            "Pʀᴇss /start ᴛᴏ ᴜsᴇ ᴍᴇ!"
        )

        sent = None

        try:

            if alive_image:

                sent = await message.reply_photo(
                    photo=alive_image,
                    caption=text
                )

            else:

                sent = await message.reply_text(
                    text
                )

            # ------------------------------------------------
            # DELETE AFTER 30 SECONDS
            # ------------------------------------------------

            await asyncio.sleep(30)

            try:
                await sent.delete()
            except Exception:
                pass

        except Exception as e:

            logger.warning(
                "Alive command failed: %s",
                e
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /trendlist
    # ========================================================

    @app.on_message(
        filters.command("trendlist")
    )
    async def trendlist_handler(
        client,
        message
    ):

        try:

            trends = await get_trending_searches(
                limit=29
            )

            if not trends:

                await message.reply_text(
                    "📊 <b>Nᴏ Tʀᴇɴᴅɪɴɢ Sᴇᴀʀᴄʜᴇs Yᴇᴛ.</b>\n\n"
                    "Sᴇᴀʀᴄʜᴇs Wɪʟʟ Aᴘᴘᴇᴀʀ Hᴇʀᴇ Wʜᴇɴ U sᴇʀs Sᴇᴀʀᴄʜ."
                )

                return

            lines = []

            for index, item in enumerate(
                trends,
                start=1
            ):

                query = item[0]

                lines.append(
                    f"{index}. {query}"
                )

            text = (
                "Tᴏᴘ 29 Tʀᴀɴᴅɪɴɢ ᴏғ ᴛʜᴇ Dᴀʏ 👇:\n\n"
                + "\n".join(lines)
                + "\n\n"
                "⚡️ 𝑨𝒍𝒍 𝒕𝒉𝒆 𝒓𝒆𝒔𝒖𝒍𝒕𝒔 𝒂𝒃𝒐𝒗𝒆 𝒄𝒐𝒎𝒆 "
                "𝒇𝒓𝒐𝒎 𝒘𝒉𝒂𝒕 𝒖𝒔𝒆𝒓𝒔 𝒉𝒂𝒗𝒆 𝒔𝒆𝒂𝒓𝒄𝒉𝒆𝒅 𝒇𝒐𝒓. "
                "𝑻𝒉𝒆𝒚'𝒓𝒆 𝒔𝒉𝒐𝒘𝒏 𝒕𝒐 𝒚𝒐𝒖 𝒆𝒙𝒂𝒄𝒕𝒍𝒚 𝒂𝒔 𝒕𝒉𝒆𝒚 𝒘𝒆𝒓𝒆 "
                "𝒔𝒆𝒂𝒓𝒄𝒉𝒆𝒅, 𝒘𝒊𝒕𝒉𝒐𝒖𝒕 𝒂𝒏𝒚 𝒄𝒉𝒂𝒏𝒈𝒆𝒔 𝒃𝒚 𝒕𝒉𝒆 𝒐𝒘𝒏𝒆𝒓."
            )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Cʟᴏsᴇ •",
                            callback_data="close_trendlist"
                        )
                    ]
                ]
            )

            await message.reply_text(
                text,
                reply_markup=buttons
            )

        except Exception as e:

            logger.exception(
                "Trendlist error: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Could not load trending searches.</b>"
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # CLOSE TRENDLIST
    # ========================================================

    @app.on_callback_query(
        filters.regex(r"^close_trendlist$")
    )
    async def close_trendlist_callback(
        client,
        callback
    ):

        try:

            await callback.message.delete()

        except Exception:

            try:
                await callback.answer(
                    "Unable to close this message.",
                    show_alert=True
                )
                return

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
    # /stats
    # ========================================================

    @app.on_message(
        filters.command("stats")
        & admin_only
    )
    async def stats_handler(
        client,
        message
    ):

        try:

            # ----------------------------------------------------
            # DATABASE STATS
            # ----------------------------------------------------
            extracting_message = await message.reply_text(
                "⏳ <b>Exᴛʀᴀᴄᴛɪɴɢ Sᴛᴀᴛs...</b>"
            )
            stats = await get_stats()

            users = stats.get(
                "users",
                0
            )

            media = stats.get(
                "media",
                0
            )

            premium_users = stats.get(
                "premium_users",
                0
            )

            used_storage = stats.get(
                "used_storage_text",
                "0.00 MB"
            )

            # ----------------------------------------------------
            # CHAT COUNT
            # ----------------------------------------------------

            chats = stats.get(
                "chats",
                0
            )

            # ----------------------------------------------------
            # RAM
            # ----------------------------------------------------

            memory = psutil.virtual_memory()

            ram_percent = memory.percent

            # ----------------------------------------------------
            # CPU
            # ----------------------------------------------------

            cpu_percent = psutil.cpu_percent(
                interval=0.5
            )

            # ----------------------------------------------------
            # DISK
            # ----------------------------------------------------

            disk = psutil.disk_usage(
                "/"
            )

            disk_percent = disk.percent

            disk_used_gb = (
                disk.used
                / (1024 ** 3)
            )

            disk_free_gb = (
                disk.free
                / (1024 ** 3)
            )

            disk_total_gb = (
                disk.total
                / (1024 ** 3)
            )

            # ----------------------------------------------------
            # PROGRESS BAR
            # ----------------------------------------------------

            def progress_bar(
                percent,
                length=10
            ):

                filled = int(
                    percent / 100 * length
                )

                filled = max(
                    0,
                    min(
                        filled,
                        length
                    )
                )

                empty = length - filled

                return (
                    "■" * filled
                    + "□" * empty
                )

            # ----------------------------------------------------
            # STATS TEXT
            # ----------------------------------------------------

            text = (

                "⌬ <b>𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 :</b>\n\n"

                f"┎ <b>›› Tᴏᴛᴀʟ Uꜱᴇʀꜱ :</b> "
                f"<b>{users:,}</b>\n"
                f"┖ <b>›› Tᴏᴛᴀʟ Cʜᴀᴛꜱ :</b> "
                f"<b>{chats:,}</b>\n\n"

                "┎ <b>›› RAM ( MEMORY ):</b>\n"
                f"┖ [{progress_bar(ram_percent)}] "
                f"<b>›› {ram_percent:.1f}%</b>\n\n"

                "┎ <b>›› CPU ( USAGE ) :</b>\n"
                f"┖ [{progress_bar(cpu_percent)}] "
                f"<b>›› {cpu_percent:.1f}%</b>\n\n"

                "┎ <b>›› DISK :</b>\n"
                f"┃ [{progress_bar(disk_percent)}] "
                f"<b>›› {disk_percent:.1f}%</b>\n"
                f"┃ <b>›› Usᴇᴅ :</b> "
                f"<b>›› {disk_used_gb:.2f} GB</b>\n"
                f"┃ <b>›› Fʀᴇᴇ :</b> "
                f"<b>›› {disk_free_gb:.2f} GB</b>\n"
                f"┖ <b>›› Tᴏᴛᴀʟ :</b> "
                f"<b>›› {disk_total_gb:.2f} GB</b>\n\n"

                "┎ <b>𝗗𝗔𝗧𝗔𝗕𝗔𝗦𝗘 𝗦𝗧𝗔𝗧𝗜𝗦𝗧𝗜𝗖𝗦 :</b>\n"
                f"┃ <b>›› Tᴏᴛᴀʟ Fɪʟᴇs :</b> "
                f"<b>›› {media:,}</b>\n"
                f"┖ <b>›› Tᴏᴛᴀʟ Sᴛᴏʀᴀɢᴇ Usᴇᴅ :</b> "
                f"<b>›› {used_storage}</b>\n\n"

                f"💎 <b>›› Pʀᴇᴍɪᴜᴍ Usᴇʀs :</b> "
                f"<b>›› {premium_users:,}</b>\n\n"

                "<b>›› Powered By: @Aero_Unity</b>"
            )

            await extracting_message.edit_text(
                text
            )
            await asyncio.sleep(30)

            try:
                await extracting_message.delete()
            except Exception:
                pass

        except Exception as e:

            logger.exception(
                "Stats error: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Could not get statistics.</b>\n\n"
                f"<code>{e}</code>"
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /premiumuser 
    # ========================================================
    @app.on_message(
        filters.command("premiumuser")
        & admin_only
    )
    async def premium_user_handler(
        client,
        message
    ):

        try:

            # ------------------------------------------------
            # GET ALL PREMIUM USERS
            # ------------------------------------------------

            import database

            cursor = database.users_collection.find(
                {
                    "premium": True
                }
            )

            premium_users = []

            async for user in cursor:
                premium_users.append(user)

            # ------------------------------------------------
            # NO PREMIUM USERS
            # ------------------------------------------------

            if not premium_users:

                await message.reply_text(
                    "<b>Pʀᴇᴍɪᴜᴍ Usᴇʀs</b>\n\n"
                    "Nᴏ Pʀᴇᴍɪᴜᴍ Usᴇʀs Fᴏᴜɴᴅ."
                )

                return

            # ------------------------------------------------
            # TOTAL PREMIUM USERS
            # ------------------------------------------------

            text = (
                " <b>Pʀᴇᴍɪᴜᴍ Usᴇʀs</b>\n\n"
                f"<b>›› Tᴏᴛᴀʟ Pʀᴇᴍɪᴜᴍ Usᴇʀs:</b> "
                f"<code>{len(premium_users)}</code>\n\n"
            )

            # ------------------------------------------------
            # USER LIST
            # ------------------------------------------------

            for index, user in enumerate(
                premium_users,
                start=1
            ):

                user_id = user.get(
                    "user_id",
                    "Unknown"
                )

                first_name = user.get(
                    "first_name",
                    "Unknown"
                )

                username = user.get(
                    "username",
                    ""
                )

                plan = user.get(
                    "plan"
                ) or "Premium"

                paid_amount = user.get(
                    "paid_amount",
                    0
                )

                premium_requests = user.get(
                    "premium_requests",
                    0
                )

                remaining = user.get(
                    "remaining_requests",
                    0
                )

                text += (
                    f"<b>{index}.</b> "
                    f"<b>›› {escape(str(first_name))}</b>\n"
                    f"<b>›› 🆔 <code>{user_id}</code></b>\n"
                )

                if username:
                    text += (
                        f"   🔹 @{escape(str(username))}\n"
                    )

                text += (
                    f"   ›› Pʟᴀɴ: <b>{escape(str(plan))}</b>\n"
                    f"   ›› Pᴀɪᴅ: <b>₹{paid_amount}</b>\n"
                    f"   ›› Pʟᴀɴ Rᴇǫᴜᴇsᴛs: "
                    f"<b>{premium_requests}</b>\n"
                    f"   ›› Rᴇᴍᴀɪɴɪɴɢ: "
                    f"<b>{remaining}</b>\n\n"
                )

                # ------------------------------------------------
                # TELEGRAM MESSAGE LIMIT
                # ------------------------------------------------

                if len(text) >= 3500:

                    await message.reply_text(
                        text
                    )

                    text = ""

            # ------------------------------------------------
            # SEND REMAINING TEXT
            # ------------------------------------------------

            if text.strip():

                await message.reply_text(
                    text
                )

        except Exception as e:

            logger.exception(
                "Premium user list error: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Could not load Premium users.</b>\n\n"
                f"<code>{escape(str(e))}</code>"
            )
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ------ Activate User ------- #

    @app.on_message(
        filters.command("activate")
        & admin_only
    )
    async def activate_handler(
        client,
        message
    ):

        if len(message.command) < 3:

            await message.reply_text(
                "<code>/activate USER_ID AMOUNT</code>\n\n"
                "<b>Example:</b>\n"
                "<code>/activate 123456789 100</code>"
            )

            return

        try:

            user_id = int(
                message.command[1]
            )

            amount = int(
                message.command[2]
            )

        except ValueError:

            await message.reply_text(
                "❌ User ID and amount must "
                "be numbers."
            )

            return

        plan = get_plan_by_amount(
            amount
        )

        if not plan:

            await message.reply_text(
                "❌ Invalid Premium plan."
            )

            return

        user = await get_user(
            user_id
        )

        if not user:

            await message.reply_text(
                "❌ User does not exist in "
                "the database.\n\n"
                "Ask the user to start the bot first."
            )

            return

        success = await activate_premium(
            user_id=user_id,
            plan_name=plan.get(
                "name",
                "Premium"
            ),
            amount=amount,
            requests=plan.get(
                "requests",
                0
            )
        )

        if not success:

            await message.reply_text(
                "❌ Premium activation failed."
            )

            return

        await message.reply_text(
            "✅ <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"

            f"<b>›› Usᴇʀ: </b> "
            f"<code>{user_id}</code>\n"

            f"<b>›› Pʟᴀɴ: </b> "
            f"<b>{plan.get('name', 'Premium')}</b>\n"

            f"<b>›› Aᴍᴏᴜɴᴛ: </b> "
            f"<b>₹{amount}</b>\n"

            f"<b>›› Rᴇǫᴜᴇsᴛs: </b> "
            f"<b>{plan.get('requests', 0)}</b>"
        )

        try:

            await client.send_message(
                user_id,

                "🎉 <b>Yᴏᴜʀ Pʟᴀɴ Is Aᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"

                f"<b>›› Pʟᴀɴ: </b> "
                f"<b>{plan.get('name', 'Premium')}</b>\n"

                f"<b>›› Pᴀɪᴅ: </b> "
                f"<b>₹{amount}</b>\n"

                f"<b>›› Mᴏᴠɪᴇ requests: </b> "
                f"<b>{plan.get('requests', 0)}</b>\n\n"

                "<b><i>✨️ Yᴏᴜ Cᴀɴ Nᴏᴡ Sᴇᴀʀᴄʜ ᴀɴᴅ Rᴇǫᴜᴇsᴛ Mᴏᴠɪᴇs, Sᴇʀɪᴇs, Dʀᴀᴍᴀs, Aɴɪᴍᴇs, TV Sᴇʀɪᴀʟs...</i></b>"
            )

        except Exception as e:

            logger.warning(
                "Could not notify user %s: %s",
                user_id,
                e
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /deactivate USER_ID
    # ========================================================

    @app.on_message(
        filters.command("deactivate")
        & admin_only
    )
    async def deactivate_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "❌ <b>Usage:</b>\n"
                "<code>/deactivate USER_ID</code>"
            )

            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ Invalid User ID."
            )

            return

        user = await get_user(
            user_id
        )

        if not user:

            await message.reply_text(
                "❌ User not found."
            )

            return

        success = await remove_premium(
            user_id
        )

        if not success:

            await message.reply_text(
                "❌ Failed to deactivate Premium."
            )

            return

        await message.reply_text(
            "✅ <b>Pʀᴇᴍɪᴜᴍ Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"
            f"<b>›› Usᴇʀ: </b> <code>{user_id}</code>"
        )

        try:

            await client.send_message(
                user_id,

                "ℹ️ <b>Pʀᴇᴍɪᴜᴍ Dᴇᴀᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"
                "<b>Sᴏʀʀʏ Tᴏ Sᴀʏ, Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ Aᴄᴄᴇss Hᴀs Bᴇᴇɴ Rᴇᴍᴏᴠᴇᴅ</b>."
            )

        except Exception as e:

            logger.warning(
                "Could not notify user %s: %s",
                user_id,
                e
            )
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /indexstatus
    # ========================================================

    @app.on_message(
        filters.command("indexstatus")
        & admin_only
    )
    async def index_status_handler(
        client,
        message
    ):

        checking_message = None

        try:

            # ----------------------------------------------------
            # INDEX STATUS IMAGE
            # ----------------------------------------------------
   
            INDEX_STATUS_IMAGE_URL = "https://graph.org/file/ab9086afb983c6cfae7d7-2d89195fff84a26ce9.jpg"

            # ----------------------------------------------------
            # CHECKING MESSAGE WITH IMAGE
            # ----------------------------------------------------

            checking_message = await client.send_photo(
                chat_id=message.chat.id,
                photo=INDEX_STATUS_IMAGE_URL,
                caption=(
                    "🔎 <b>ᴄʜᴇᴄᴋɪɴɢ ɪɴᴅᴇx ғɪʟᴇs...</b>"
                )
            )

            # ----------------------------------------------------
            # GET INDEXER STATE
            # ----------------------------------------------------

            state = await get_indexer_state()

            last_message = state.get(
                "last_message_id",
                0
            )

            # ----------------------------------------------------
            # GET REAL MONGODB MEDIA STATISTICS
            # ----------------------------------------------------

            storage = await get_media_storage_stats()

            total_files = storage.get(
                "total_files",
                0
            )

            total_size = storage.get(
                "total_size",
                0
            )

            # ----------------------------------------------------
            # CONVERT BYTES
            # ----------------------------------------------------

            if total_size >= 1024 ** 3:

                size_text = (
                    f"{total_size / (1024 ** 3):.2f} GB"
                )

            elif total_size >= 1024 ** 2:
  
                size_text = (
                     f"{total_size / (1024 ** 2):.2f} MB"
                 )

            elif total_size >= 1024:

                size_text = (
                    f"{total_size / 1024:.2f} KB"
                )

            else:

                 size_text = (
                     f"{total_size} B"
                 )

            # ----------------------------------------------------
            # FINAL STATUS
            # ----------------------------------------------------

            await checking_message.edit_caption(

                caption=(
                    "📚 <b>Iɴᴅᴇxᴇʀ Sᴛᴀᴛᴜs</b>\n\n"

                    f"<b>›› Tᴏᴛᴀʟ Iɴᴅᴇxᴇᴅ Fɪʟᴇs:</b> "
                    f"<b>{total_files:,}</b>\n\n"

                    f"<b>›› Tᴏᴛᴀʟ Iɴᴅᴇxᴇᴅ Sᴛᴏʀᴀɢᴇ:</b> "
                    f"<b>{size_text}</b>\n\n"

                    f"<b>›› Lᴀsᴛ Mᴇssᴀɢᴇ ID:</b> "
                    f"<code>{last_message}</code>\n\n"

                    "<b>›› Pᴏᴡᴇʀᴇᴅ Bʏ : @Aero_Unity</b>"
                )
            )

            # ----------------------------------------------------
            # WAIT 30 SECONDS
            # ----------------------------------------------------

            await asyncio.sleep(30)

            # ----------------------------------------------------
            # DELETE STATUS MESSAGE
            # ----------------------------------------------------

            try:
                await checking_message.delete()
            except Exception:
                pass

            # ----------------------------------------------------
            # DELETE /indexstatus COMMAND
            # ----------------------------------------------------

            try:
                await message.delete()
            except Exception:
                pass

        except Exception as e:
            logger.exception(
                "Indexer status error: %s",
                e
            )

            # ----------------------------------------------------
            # ERROR MESSAGE
            # ----------------------------------------------------

            if checking_message:

                try:

                    await checking_message.edit_caption(
                        caption=(
                            "❌ <b>Could not get indexer status.</b>\n\n"
                            f"<code>{e}</code>"
                        )
                    )

                    await asyncio.sleep(30)

                    try:
                        await checking_message.delete()
                    except Exception:
                        pass

                except Exception:
                    pass

            else:

                try:

                    error_message = await message.reply_text(
                        "❌ <b>Could not get indexer status.</b>\n\n"
                        f"<code>{e}</code>"
                    )

                    await asyncio.sleep(30)

                    try:
                        await error_message.delete()
                    except Exception:
                        pass

                except Exception:
                    pass

        # ----------------------------------------------------
        # DELETE /indexstatus COMMAND
        # ----------------------------------------------------

        try:
            await message.delete()
        except Exception:
            pass
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /resetindex
    # ========================================================

    @app.on_message(
        filters.command("resetindex")
        & admin_only
    )
    async def reset_index_handler(
        client,
        message
    ):

        try:

            from database import (
                reset_indexer
            )

            await reset_indexer()

            await message.reply_text(
                "✅ <b>Iɴᴅᴇxᴇʀ Pᴏsɪᴛɪᴏɴ Rᴇsᴇᴛ.</b>\n\n"
                "<b>Tʜᴇ Nᴇxᴛ Iɴᴅᴇxɪɴɢ Rᴜɴ ᴡɪʟʟ Sᴛᴀʀᴛ "
                "Fʀᴏᴍ Tʜᴇ Bᴇɢɪɴɴɪɴɢ</b>"
            )

        except Exception as e:
            logger.exception(
                "Reset index error: %s",
                e
            )

            await message.reply_text(
                "❌ Failed to reset indexer."
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /id
    # ========================================================

    @app.on_message(
        filters.command("id")
    )
    async def id_handler(
        client,
        message
    ):

        user_id = message.from_user.id

        await message.reply_text(
            "<b>Your Telegram ID</b>\n\n"
            f"ID - <code>{user_id}</code>"
        )

    # ========================================================
    # /info
    # ========================================================

    @app.on_message(
        filters.command("info")
    )
    async def info_handler(
        client,
        message
    ):

        # ----------------------------------------------------
        # GET TARGET USER
        # ----------------------------------------------------

        target_user = None

        try:

            # /info by reply
            if message.reply_to_message:

                if message.reply_to_message.from_user:

                    target_user = message.reply_to_message.from_user

            # /info USER_ID
            elif len(message.command) > 1:

                target_user = await client.get_users(
                    message.command[1]
                )

            # /info by sender
            else:

                target_user = message.from_user

        except Exception as e:

            logger.exception(
                "Could not get info user: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Could not fetch user information.</b>\n\n"
                f"<code>{escape(str(e))}</code>"
            )

            return

        if not target_user:

            await message.reply_text(
                "❌ <b>User not found.</b>"
            )

            return

        # ----------------------------------------------------
        # FETCHING MESSAGE
        # ----------------------------------------------------

        fetching = await message.reply_text(
            "⏳ <b>Fᴇᴛᴄʜɪɴɢ Uꜱᴇʀ Iɴғᴏ...</b>"
        )

        await asyncio.sleep(0.1)

        try:
            await fetching.delete()
        except Exception:
            pass

        # ----------------------------------------------------
        # PROCESSING MESSAGE
        # ----------------------------------------------------

        processing = await message.reply_text(
            " <b>Pʀᴏᴄᴇꜱꜱɪɴɢ Uꜱᴇʀ Iɴғᴏ...</b>"
        )

        await asyncio.sleep(0.5)

        try:
            await processing.delete()
        except Exception:
            pass

        # ----------------------------------------------------
        # USER DETAILS
        # ----------------------------------------------------

        user_id = target_user.id

        first_name = target_user.first_name or "None"
        last_name = target_user.last_name or "None"

        username = target_user.username

        if username:
            username_text = f"@{username}"
            username_link = (
                f"https://t.me/{username}"
            )
        else:
            username_text = "None"
            username_link = (
                f"tg://user?id={user_id}"
            )

        user_link = f"tg://user?id={user_id}"

        # ----------------------------------------------------
        # CLICKABLE FIRST NAME
        # ----------------------------------------------------

        clickable_first_name = (
            f'<a href="tg://user?id={user_id}">'
            f'{escape(str(first_name))}'
            f'</a>'
        )

        # ----------------------------------------------------
        # CLICKABLE USERNAME
        # ----------------------------------------------------

        clickable_username = (
            f'<a href="{username_link}">'
            f'{escape(username_text)}'
            f'</a>'
        )

        # ----------------------------------------------------
        # CLICKABLE USER LINK
        # ----------------------------------------------------

        clickable_user_link = (
            f'<a href="{user_link}">Cʟɪᴄᴋ Hᴇʀᴇ</a>'
        )

        # ----------------------------------------------------
        # DATA CENTRE
        # ----------------------------------------------------

        dc_id = getattr(
            target_user,
            "dc_id",
            None
        )

        if dc_id is None:
            dc_id = "Unknown"

        # ----------------------------------------------------
        # FINAL INFO TEXT
        # ----------------------------------------------------

        text = (
            f"›› <b>Fɪʀsᴛ Nᴀᴍᴇ:</b> "
            f"{clickable_first_name}\n"

            f"›› <b>Lᴀsᴛ Nᴀᴍᴇ:</b> "
            f"{escape(str(last_name))}\n"

            f"›› <b>Tᴇʟᴇɢʀᴀᴍ ID:</b> "
            f"<code>{user_id}</code>\n"

            f"›› <b>Dᴀᴛᴀ Cᴇɴᴛʀᴇ:</b> "
            f"<code>{dc_id}</code>\n"

            f"›› <b>Uꜱᴇʀ Nᴀᴍᴇ:</b> "
            f"{clickable_username}\n"

            f"›› <b>Uꜱᴇʀ 𝖫𝗂𝗇𝗄:</b> "
            f"{clickable_user_link}"
        )

        # ----------------------------------------------------
        # CLOSE BUTTON
        # ----------------------------------------------------

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "• Cʟᴏsᴇ •",
                        callback_data=f"close_info_{user_id}"
                    )
                ]
            ]
        )

        # ----------------------------------------------------
        # PROFILE PHOTO
        # ----------------------------------------------------

        try:

            photos = []

            async for photo in client.get_chat_photos(
                user_id,
                limit=1
            ):
                photos.append(photo)

            if photos:

                await message.reply_photo(
                    photo=photos[0].file_id,
                    caption=text,
                    reply_markup=buttons
                )

            else:

                await message.reply_text(
                    text,
                    reply_markup=buttons
                )

        except Exception as e:

            logger.warning(
                "Could not fetch profile photo: %s",
                e
            )

            await message.reply_text(
                text,
                reply_markup=buttons
            )

    # ========================================================
    # CLOSE USER INFO
    # ========================================================

    @app.on_callback_query(
        filters.regex(r"^close_info_\d+$")
    )
    async def close_info_callback(
        client,
        callback
    ):

        try:

            await callback.message.delete()

        except Exception:

            pass

        try:

            await callback.answer()

        except Exception:

            pass
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /broadcast
    # ========================================================
   
    @app.on_message(
        filters.command("broadcast")
        & admin_only
    )
    async def broadcast_handler(
        client,
        message
    ):

        if not message.reply_to_message:

            await message.reply_text(
                "❌ <b>Reply to the message you want to broadcast.</b>"
            )

            return

        source = message.reply_to_message

        status = await message.reply_text(
            "<b>Bʀᴏᴀᴅᴄᴀsᴛ Sᴛᴀʀᴛᴇᴅ...</b>"
        )

        # ----------------------------------------------------
        # GET ALL USERS
        # ----------------------------------------------------
    
        try:

            user_ids = await get_all_user_ids()

        except Exception as e:

            logger.exception(
                "Failed to get users for broadcast: %s",
                e
            )

            await status.edit_text(
                "❌ <b>Broadcast Failed</b>\n\n"
                "Could not get users from the database."
            )
  
            return

        # ----------------------------------------------------
        # REMOVE INVALID / DUPLICATE IDS
        # ----------------------------------------------------

        clean_user_ids = []
        seen = set()

        for user_id in user_ids:

            try:

                user_id = int(user_id)
   
                if user_id not in seen:

                    seen.add(user_id)
                    clean_user_ids.append(user_id)

            except (TypeError, ValueError):

                continue
  
        user_ids = clean_user_ids

        total = len(user_ids)

        if total == 0:

            await status.edit_text(
                "❌ <b>No users found.</b>"
            )

            return
  
        success = 0
        processed = 0

        for user_id in user_ids:

            try:

                await client.copy_message(
                    chat_id=user_id,
                    from_chat_id=source.chat.id,
                    message_id=source.id,
                    reply_markup=source.reply_markup
                )

                success += 1

            except Exception as e:

                logger.warning(
                    "Broadcast skipped for user %s: %s",
                    user_id,
                    repr(e)
                )

            processed += 1

            await asyncio.sleep(0.05)

            if processed % 25 == 0:

                try:

                    await status.edit_text(
                        "📢 <b>Bʀᴏᴀᴅᴄᴀsᴛɪɴɢ...</b>\n\n"

                        f"👥 <b>Tᴏᴛᴀʟ Usᴇʀs:</b> "
                        f"<code>{total}</code>\n\n"

                        f"✅ <b>Sᴇɴᴛ:</b> "
                        f"<code>{success}</code>\n\n"

                        f"📊 <b>Pʀᴏᴄᴇssᴇᴅ:</b> "
                        f"<code>{processed}/{total}</code>"
                    )

                except Exception:
                    pass

        # ----------------------------------------------------
        # FINAL RESULT
        # ----------------------------------------------------

        try:

            await status.edit_text(
                "📢 <b>Bʀᴏᴀᴅᴄᴀsᴛ Cᴏᴍᴘʟᴇᴛᴇᴅ!</b>\n\n"

                f"👥 <b>Tᴏᴛᴀʟ Usᴇʀs:</b> "
                f"<code>{total}</code>\n\n"

                f"✅ <b>Sᴜᴄᴄᴇssғᴜʟʟʏ Sᴇɴᴛ:</b> "
                f"<code>{success}</code>\n\n"

                f"📊 <b>Cᴏᴍᴘʟᴇᴛᴇᴅ:</b> "
                f"<code>{processed}/{total}</code>"
            )

        except Exception:
            pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ============================================================
    # /clearjunk
    # ============================================================

    @app.on_message(
        filters.command("clearjunk")
        & admin_only
    )
    async def clear_junk_handler(client, message):

        if message.chat.type != ChatType.PRIVATE:
            return await message.reply_text(
                "❌ <b>This command can only be used in Bot PM.</b>"
        )

        status = await message.reply_text(
            "🧹 <b>Cʟᴇᴀɴɪɴɢ Lᴀsᴛ 200 Mᴇssᴀɢᴇs...</b>"
        )

        deleted = 0

        try:
                
            start_id = max(1, message.id - 200)
            end_id = message.id

            message_ids = list(
                range(start_id, end_id + 1)
            )

            for i in range(0, len(message_ids), 100):

                batch = message_ids[i:i + 100]

                try:
                    result = await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=batch
                    )

                    if isinstance(result, list):
                        deleted += len(result)
                    else:
                        deleted += len(batch)

                except Exception as e:
                    logger.warning(
                        f"Clear junk batch failed: {e}"
                    )
 
            try:
                await status.delete()
            except Exception:
                pass

            try:
                await message.reply_text(
                    "🧹 <b>Cʟᴇᴀɴᴜᴘ Cᴏᴍᴘʟᴇᴛᴇ</b>\n\n"
                    f"🗑 <b>Mᴇssᴀɢᴇs Dᴇʟᴇᴛᴇᴅ:</b> "
                    f"<code>{deleted}</code>"
                )
     
            except Exception as e:
                logger.warning(
                    f"Clear junk result message failed: {e}"
                )

        except Exception as e:
            logger.exception(
                f"Clear junk error: {e}"
            )

            try:
                await status.edit_text(
                    "❌ <b>Cʟᴇᴀɴᴜᴘ Fᴀɪʟᴇᴅ</b>\n\n"
                    f"<code>{str(e)}</code>"
                )
            except Exception:
                pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ============================================================
    # /clearjunkgroup
    # ============================================================

    @app.on_message(
        filters.command("clearjunkgroup")
        & admin_only
    )
    async def clear_junk_group_handler(client, message):

        if message.chat.type not in [
            ChatType.GROUP,
            ChatType.SUPERGROUP
        ]:
            await message.reply_text(
                "❌ <b>This command can only be used in a group.</b>"
            )
            return

        status = await message.reply_text(
            "🧹 <b>Cʟᴇᴀɴɪɴɢ Lᴀsᴛ 500 Mᴇssᴀɢᴇs...</b>"
        )

        deleted = 0

        try:
        
            start_id = max(1, message.id - 500)
            end_id = message.id
    
            message_ids = list(
                range(start_id, end_id + 1)
            )

            # Delete in batches of 100.
            for i in range(0, len(message_ids), 100):

                batch = message_ids[i:i + 100]

                try:
                    result = await client.delete_messages(
                        chat_id=message.chat.id,
                        message_ids=batch
                    )

                    if isinstance(result, list):
                        deleted += len(result)
                    else:
                        deleted += len(batch)
  
                except Exception as e:
                    logger.warning(
                        f"Clear group batch failed: {e}"
                    )

            try:
                await status.delete()
            except Exception:
                pass

            try:
                await message.reply_text(
                    "🧹 <b>Gʀᴏᴜᴘ Cʟᴇᴀɴᴜᴘ Cᴏᴍᴘʟᴇᴛᴇ</b>\n\n"
                    f"🗑 <b>Mᴇssᴀɢᴇs Dᴇʟᴇᴛᴇᴅ:</b> "
                    f"<code>{deleted}</code>"
                )

            except Exception as e:
                logger.warning(
                    f"Clear group result message failed: {e}"
            )

        except Exception as e:
            logger.exception(
                f"Clear junk group error: {e}"
            )

            try:
                await status.edit_text(
                    "❌ <b>Gʀᴏᴜᴘ Cʟᴇᴀɴᴜᴘ Fᴀɪʟᴇᴅ</b>\n\n"
                    f"<code>{str(e)}</code>"
                )
            except Exception:
                pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # OWNER ONLY CHECK
    # ========================================================

    def owner_only(_, __, message):

        return (
            message.from_user is not None
            and message.from_user.id == OWNER_ID
        )

    owner_only_filter = filters.create(
        owner_only
    )


    # ========================================================
    # /addadmin
    # ========================================================

    @app.on_message(
        filters.command("addadmin")
        & owner_only_filter
    )
    async def add_admin_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "❌ <b>Usage:</b>\n"
                "<code>/addadmin USER_ID</code>"
            )
            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ <b>Invalid User ID.</b>"
            )
            return

        if user_id == OWNER_ID:

            await message.reply_text(
                "❌ <b>Owner is already the owner.</b>"
            )
            return

        existing = await get_admin(
            user_id
        )

        if existing:

            await message.reply_text(
                "⚠️ <b>This user is already an admin.</b>"
            )
            return

        try:

            user = await client.get_users(
                user_id
            )

            first_name = (
                user.first_name or ""
            )

            username = (
                user.username or ""
            )

        except Exception:

            first_name = ""
            username = ""

        success = await add_admin(
            user_id=user_id,
            added_by=message.from_user.id,
            first_name=first_name,
            username=username
        )

        if not success:

            await message.reply_text(
                "❌ <b>Failed to add admin.</b>"
            )
            return

        if user_id not in ADMIN_IDS:

            ADMIN_IDS.add(user_id)

        # ------------------------------------------------
        # NOTIFY OWNER
        # ------------------------------------------------

        await message.reply_text(
            "✅ <b>Aᴅᴍɪɴ Aᴅdᴇᴅ</b>\n\n"
            f"›› 🆔 <code>{user_id}</code>\n"
            f"›› Nᴀᴍᴇ: <b>{escape(first_name or 'Unknown')}</b>\n"
            + (
                f"›› Uꜱᴇʀɴᴀᴍᴇ: "
                f"<b>@{escape(username)}</b>"
                if username
                else ""
            )
        )

        # ------------------------------------------------
        # NOTIFY NEW ADMIN
        # ------------------------------------------------

        try:

            await client.send_message(
                user_id,

                "👑 <b>Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Aᴅᴅᴇᴅ Aꜱ Aɴ Aᴅᴍɪɴ</b>\n\n"

                "🎉 <b>Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴs!</b>\n\n"

                "<b>Yᴏᴜ Hᴀᴠᴇ Bᴇᴇɴ Sᴜᴄᴄᴇssғᴜʟʟʏ Aᴅᴅᴇᴅ "
                "Aꜱ Aɴ Aᴅᴍɪɴ Oғ Tʜɪs Bᴏᴛ.</b>\n\n"

                "<b>Yᴏᴜ Cᴀɴ Nᴏᴡ Uѕᴇ Tʜᴇ Aᴠᴀɪʟᴀʙʟᴇ Aᴅᴍɪɴ Cᴏᴍᴍᴀɴᴅs.</b>"
            )

        except Exception as e:

            logger.warning(
                "Could not notify new admin %s: %s",
                user_id,
                e
            )


    # ========================================================
    # /removeadmin
    # ========================================================

    @app.on_message(
        filters.command("removeadmin")
        & owner_only_filter
    )
    async def remove_admin_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "❌ <b>Usage:</b>\n"
                "<code>/removeadmin USER_ID</code>"
            )
            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ <b>Invalid User ID.</b>"
            )
            return

        if user_id == OWNER_ID:

            await message.reply_text(
                "❌ <b>You cannot remove the owner.</b>"
            )
            return

        success = await remove_admin(
            user_id
        )

        if not success:

            await message.reply_text(
                "❌ <b>This user is not a saved admin.</b>"
            )
            return

        while user_id in ADMIN_IDS:

            ADMIN_IDS.remove(
                user_id
            )

        await message.reply_text(
            "✅ <b>Aᴅᴍɪɴ Rᴇᴍᴏᴠᴇᴅ</b>\n\n"
            f"›› 🆔 <code>{user_id}</code>"
        )


    # ========================================================
    # /adminlist
    # ========================================================

    @app.on_message(
        filters.command("adminlist")
        & owner_only_filter
    )
    async def admin_list_handler(
        client,
        message
    ):

        try:

            admins = await get_admins()

            if not admins:

                sent = await message.reply_text(
                    "👑 <b>Aᴅᴍɪɴ Lɪsᴛ</b>\n\n"
                    "Nᴏ Aᴅᴍɪɴs Fᴏᴜɴᴅ.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "• Cʟᴏsᴇ •",
                                    callback_data="close_adminlist"
                                )
                            ]
                        ]
                    )
                )

                await asyncio.sleep(30)

                try:
                    await sent.delete()
                except Exception:
                    pass

                return

            lines = [
                "👑 <b>Aᴅᴍɪɴ Lɪsᴛ</b>\n"
            ]

            for index, admin in enumerate(
                admins,
                start=1
            ):

                user_id = admin.get(
                    "user_id"
                )

                first_name = (
                    admin.get("first_name")
                    or "Unknown"
                )

                username = (
                    admin.get("username")
                    or ""
                )

                name_link = (
                    f'<a href="tg://user?id={user_id}">'
                    f'{escape(str(first_name))}</a>'
                )

                lines.append(
                    f"<b>{index}. {name_link}</b>\n"
                    f"   🆔 <code>{user_id}</code>"
                )

                if username:

                    lines.append(
                        f"   • <a href=\"https://t.me/"
                        f"{escape(str(username))}\">"
                        f"@{escape(str(username))}</a>"
                    )

                lines.append("")

            text = "\n".join(
                lines
            )

            buttons = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Cʟᴏsᴇ •",
                            callback_data="close_adminlist"
                        )
                    ]
                ]
            )

            sent = None

            # ------------------------------------------------
            # TRY FIRST ADMIN PROFILE PHOTO
            # ------------------------------------------------

            try:

                first_admin = admins[0].get(
                    "user_id"
                )

                photos = []

                async for photo in client.get_chat_photos(
                    first_admin,
                    limit=1
                ):

                    photos.append(
                        photo
                    )

                if photos:

                    sent = await message.reply_photo(
                        photo=photos[0].file_id,
                        caption=text,
                        reply_markup=buttons
                    )

            except Exception as e:

                logger.warning(
                    "Admin list photo failed: %s",
                    e
                )

            if sent is None:

                sent = await message.reply_text(
                    text,
                    reply_markup=buttons
                )

            await asyncio.sleep(30)

            try:
                await sent.delete()
            except Exception:
                pass

        except Exception as e:

            logger.exception(
                "Admin list error: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Could not load admin list.</b>\n\n"
                f"<code>{escape(str(e))}</code>"
            )


    # ========================================================
    # CLOSE ADMIN LIST
    # ========================================================

    @app.on_callback_query(
        filters.regex(r"^close_adminlist$")
    )
    async def close_admin_list_callback(
        client,
        callback
    ):

        if (
            callback.from_user is None
            or callback.from_user.id != OWNER_ID
        ):

            await callback.answer(
                "❌ Owner only.",
                show_alert=True
            )
            return

        try:

            await callback.message.delete()

        except Exception:
            pass

        try:

            await callback.answer()

        except Exception:
            pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # /warn
    # ========================================================

    @app.on_message(
        filters.command("warn")
        & owner_only_filter
    )
    async def warn_handler(
        client,
        message
    ):

        if len(message.command) < 2:

            await message.reply_text(
                "❌ <b>Usage:</b>\n"
                "<code>/warn USER_ID [REASON]</code>"
            )
            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ <b>Invalid User ID.</b>"
            )
            return

        user = await get_user(
            user_id
        )

        if not user:

            await message.reply_text(
                "❌ <b>User not found.</b>"
            )
            return

        reason = " ".join(
            message.command[2:]
        ).strip()

        warnings = await add_warning(
            user_id=user_id,
            warned_by=message.from_user.id,
            reason=reason
        )

        if warnings is None:

            await message.reply_text(
                "❌ <b>Failed to add warning.</b>"
            )
            return

        await message.reply_text(
            "⚠️ <b>Wᴀʀɴɪɴɢ Aᴅᴅᴇᴅ</b>\n\n"
            f"›› 🆔 <code>{user_id}</code>\n"
            f"›› Wᴀʀɴɪɴɢs: "
            f"<b>{warnings}</b>\n"
            f"›› Rᴇᴀsᴏɴ: "
            f"<b>{escape(reason or 'No reason')}</b>"
        )

        try:

            await client.send_message(
                user_id,

                "⚠️ <b>Yᴏᴜ Hᴀᴠᴇ Rᴇᴄᴇɪᴠᴇᴅ A Wᴀʀɴɪɴɢ</b>\n\n"
                f"›› Wᴀʀɴɪɴɢs: <b>{warnings}</b>\n"
                f"›› Rᴇᴀsᴏɴ: "
                f"<b>{escape(reason or 'No reason')}</b>"
            )

        except Exception as e:

            logger.warning(
                "Could not notify warned user %s: %s",
                user_id,
                e
            )
    # ==========================
    # /unwarn
    # ==========================
    @app.on_message(
        filters.command("unwarn")
         & owner_only_filter
    )
    async def unwarn_handler(
        client,
        message
    ):
        if len(message.command) < 2:
            await message.reply_text(
                "<code>/unwarn USER_ID</code>"
            )
            return

        try:
            user_id = int(message.command[1])
        except ValueError:
            await message.reply_text(
                "❌ <b>Invalid User ID.</b>"
            )
            return

        user = await get_user(user_id)

        if not user:
            await message.reply_text(
                "❌ <b>User not found.</b>"
            )
            return

        current_warnings = await get_warnings(user_id)

        if current_warnings <= 0:
            await message.reply_text(
                "⚠️ <b>This user has no warnings.</b>"
            )
            return

        success = await remove_warning(user_id)

        if not success:
            await message.reply_text(
                "❌ <b>Failed to remove warning.</b>"
            )
            return

        remaining = await get_warnings(user_id)

        await message.reply_text(
            "✅ <b>Wᴀʀɴɪɴɢ Rᴇᴍᴏᴠᴇᴅ</b>\n\n"
            f"›› 🆔 <code>{user_id}</code>\n"
            f"<b>›› Rᴇᴍᴀɪɴɪɴɢ Wᴀʀɴɪɴɢs: </b> "
            f"<b>{remaining}</b>"
        )

        try:
            await client.send_message(
                user_id,
                "✅ <b>Wᴀʀɴɪɴɢ Rᴇᴍᴏᴠᴇᴅ</b>\n\n"
                f"<b>›› Rᴇᴍᴀɪɴɪɴɢ Wᴀʀɴɪɴɢs: </b> "
                f"<b>{remaining}</b>"
            )
        except Exception as e:
            logger.warning(
                "Could not notify user %s about removed warning: %s",
                user_id,
                e
            )
    # ==========================
    # /warningslist
    # ==========================
    @app.on_message(
        filters.command("warningslist")
        & owner_only_filter
    )
    async def warnings_list_handler(
        client,
        message
    ):
        try:
            warnings = await get_all_warnings()

            keyboard = InlineKeyboardMarkup(
                [[
                        InlineKeyboardButton(
                            "• Cʟᴏsᴇ •",
                            callback_data="warnings_close"
                        )
                ]]
            )

            if not warnings:
                await message.reply_text(
                    "⚠️ <b>Wᴀʀɴɪɴɢs Lɪsᴛ</b>\n\n"
                    "<b>✅ Nᴏ Uꜱᴇʀs Cᴜʀʀᴇɴᴛʟʏ Hᴀᴠᴇ Wᴀʀɴɪɴɢs.</b>",
                    reply_markup=keyboard
                )
                return

            lines = [
                "⚠️ <b>Wᴀʀɴɪɴɢs Lɪsᴛ</b>\n"
            ]

            for index, user in enumerate(
                warnings,
                start=1
            ):
                user_id = user.get(
                    "user_id",
                    "Unknown"
                )

                first_name = user.get(
                    "first_name"
                ) or "Unknown"

                username = user.get(
                    "username"
                ) or ""

                warning_count = int(
                    user.get("warnings", 0) or 0
                )

                name_link = (
                    f'<a href="tg://user?id={user_id}">'
                    f'{escape(str(first_name))}'
                    f'</a>'
                )

                lines.append(
                    f"<b>{index}. {name_link}</b>\n"
                    f"    🆔 <code>{user_id}</code>\n"
                    f"<b>⚠️ Wᴀʀɴɪɴɢs:</b> "
                    f"<b>{warning_count}</b>"
                )

                if username:
                    lines.append(
                        f"   • @{escape(str(username))}"
                    )

                lines.append("")

            text = "\n".join(lines)

            if len(text) > 3900:
                text = (
                    text[:3850]
                    + "\n\n"
                    "⚠️ <b>Lɪsᴛ Tʀᴜɴᴄᴀᴛᴇᴅ Dᴜᴇ Tᴏ Mᴇssᴀɢᴇ Lɪᴍɪᴛ.</b>"
                )

            await message.reply_text(
                text,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.exception(
                "Warnings list error: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Failed to load warnings list.</b>\n\n"
                f"<code>{escape(str(e))}</code>"
            )

    # =========================
    # callback of wraning close 
    # ==========================

    @app.on_callback_query(
        filters.regex(r"^warnings_close$")
    )
    async def warnings_close_callback(
        client,
        callback
    ):
        if (
            callback.from_user is None
            or callback.from_user.id != OWNER_ID
        ):
            await callback.answer(
                "‼️ Owner only can use the command.",
                show_alert=True
            )
            return

        try:
            await callback.message.delete()
        except Exception:
            pass

        try:
            await callback.answer()
        except Exception:
            pass

    # ========================================================
    # /reload
    # ========================================================

    @app.on_message(
        filters.command("reload")
        & owner_only_filter
    )
    async def reload_handler(
        client,
        message
    ):

        reload_message = None

        try:

            reload_message = await message.reply_text(
                "⚡️"
            )

            await asyncio.sleep(1.2)

            await reload_message.edit_text(
                "⏳ <b>Pʟᴇᴀsᴇ Wᴀɪᴛ...</b>"
            )

            await asyncio.sleep(1)

            importlib.reload(
                config
            )

            await reload_message.edit_text(
                "♻️ <b>Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴ Rᴇʟᴏᴀᴅᴇᴅ</b>\n\n"
                "<b>›› Bot Is Restarted.</b>\n"
                "<b>›› Admin List Updated.</b>\n\n"
                "<b>Powered By: @Aero_Unity</b>"
            )

            await asyncio.sleep(30)

            try:
                await reload_message.delete()
            except Exception:
                pass

        except Exception as e:

            logger.exception(
                "Reload error: %s",
                e
            )

            if reload_message:

                try:

                    await reload_message.edit_text(
                        "❌ <b>Cᴏɴғɪɢᴜʀᴀᴛɪᴏɴ Rᴇʟᴏᴀᴅ Fᴀɪʟᴇᴅ</b>\n\n"
                        f"<code>{escape(str(e))}</code>"
                    )

                    await asyncio.sleep(30)

                    try:
                        await reload_message.delete()
                    except Exception:
                        pass

                except Exception:
                    pass

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ============================================================
    # /optimize
    # ============================================================

    @app.on_message(
        filters.command("optimize")
        & admin_only
    )
    async def optimize_handler(client, message):

        status_message = await message.reply_text(
            "<b>›› Pʟᴇᴀsᴇ Wᴀɪᴛ...</b>"
        )

        try:

            result = await optimize_database()

            text = (
                "⚡ <b>Dᴀᴛᴀʙᴀsᴇ Oᴘᴛɪᴍɪᴢᴇᴅ</b>\n\n"
                f"👤 Usᴇʀs: <code>{result['users']:,}</code>\n"
                f"💬 Cʜᴀᴛs: <code>{result['chats']:,}</code>\n"
                f"📁 Fɪʟᴇs: <code>{result['files']:,}</code>\n"
                f"🧹 Sᴇssɪᴏɴs Cʟᴇᴀɴᴇᴅ: <code>{result['sessions_cleaned']}</code>\n\n"
                "✅ <b>Cᴏᴍᴘʟᴇᴛᴇᴅ</b>"
            )
            
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Cʟᴏsᴇ •",
                            callback_data="optimize_close"
                        )
                    ]
                ]
            )

            await status_message.edit_text(
                text,
                reply_markup=keyboard
            )

        except Exception as e:

            logger.exception(
                "Database optimization failed: %s",
                e
            )

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Cʟᴏsᴇ •",
                            callback_data="optimize_close"
                        )
                    ]
                ]
            )
  
            await status_message.edit_text(
                "❌ <b>Dᴀᴛᴀʙᴀsᴇ Oᴘᴛɪᴍɪᴢᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ</b>\n\n"
                f"<code>{escape(str(e))}</code>",
                reply_markup=keyboard
            )
            
    # ============================================================
    # OPTIMIZE CLOSE BUTTON
    # ============================================================

    @app.on_callback_query(
        filters.regex("^optimize_close$")
    )
    async def optimize_close_callback(client, callback):

        if not is_admin(callback.from_user.id):
             await callback.answer(
                 "‼️ You are not authorized.",
                 show_alert=True
             )
             return

        try:
            await callback.message.delete()
            await callback.answer()

        except Exception:
            await callback.answer(
                "❌ Unable to close.",
                show_alert=True
            )
   
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
