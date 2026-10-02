# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #

import os
import asyncio
import logging
import requests

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #

# ============================================================
# CONFIG
# ============================================================

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #

# ============================================================
# SMALL CAPS
# ============================================================

SMALL_CAPS = str.maketrans(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
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

# ============================================================
# CATBOX
# ============================================================

async def upload_to_catbox(file_path):

    try:

        if not file_path or not os.path.exists(file_path):

            return None

        with open(file_path, "rb") as f:

            response = await asyncio.to_thread(
                requests.post,
                "https://catbox.moe/user/api.php",
                data={
                    "reqtype": "fileupload"
                },
                files={
                    "fileToUpload": f
                },
                timeout=120
            )

        if response.status_code != 200:

            logging.error(
                "Catbox HTTP %s: %s",
                response.status_code,
                response.text[:1000]
            )

            return None

        result = response.text.strip()

        if (
            result.startswith("https://")
            or
            result.startswith("http://")
        ):

            return result

        logging.error(
            "Unexpected Catbox response: %s",
            result
        )

    except Exception as e:

        logging.exception(
            "Catbox upload error: %s",
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
# REGISTER HANDLERS
# ============================================================

def register_telegraph_handlers(app):

    # ========================================================
    # /TELEGRAPH COMMAND
    # ========================================================

    @app.on_message(
        filters.command("telegraph") & filters.reply
    )
    async def telegraph_handler(
        client,
        message
    ):

        replied = message.reply_to_message

        if not replied or not replied.photo:

            await message.reply_text(
                " <b>ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ.</b>"
            )

            return

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status = await message.reply_text(
            "<b>›› ᴡᴀɪᴛ ᴀ sᴇᴄ...</b>"
        )

        file_path = None

        try:

            os.makedirs(
                "downloads",
                exist_ok=True
            )

            # ------------------------------------------------
            # DOWNLOAD IMAGE
            # ------------------------------------------------

            file_path = await client.download_media(
                replied.photo,
                file_name=(
                    f"downloads/"
                    f"catbox_"
                    f"{message.chat.id}_"
                    f"{message.id}.jpg"
                )
            )

            if not file_path:

                await status.edit_text(
                    "❌ <b>Failed to download image.</b>"
                )

                return

            # ------------------------------------------------
            # FILE SIZE
            # ------------------------------------------------

            file_size = os.path.getsize(
                file_path
            )

            size_mb = (
                file_size
                / (1024 * 1024)
            )

            # ------------------------------------------------
            # SESSION STORAGE
            # ------------------------------------------------

            if not hasattr(
                client,
                "_catbox_files"
            ):

                client._catbox_files = {}

            user_id = (
                message.from_user.id
                if message.from_user
                else message.chat.id
            )

            client._catbox_files[
                status.id
            ] = {

                "file_path": file_path,

                "user_id": user_id,

                "created_at": (
                    asyncio.get_running_loop().time()
                )

            }

            # ------------------------------------------------
            # BUTTON
            # ------------------------------------------------

            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Cᴀᴛʙᴏx •",
                            callback_data="catbox_upload"
                        )
                    ]
                ]
            )

            await status.edit_text(
                "<b>Iᴍᴀɢᴇ Rᴇᴀᴅʏ</b>\n\n"
                f"<b>›› Sɪᴢᴇ: {size_mb:.2f} MB</b>\n\n"
                "<b>☏ Cʜᴏᴏsᴇ ᴀ Sᴇʀᴠɪᴄᴇ:",
                reply_markup=keyboard
            )

        except Exception as e:

            logging.exception(
                "Catbox image preparation error: %s",
                e
            )

            if file_path and os.path.exists(file_path):

                try:
                    os.remove(file_path)
                except Exception:
                    pass

            await status.edit_text(
                "❌ <b>Failed to prepare image.</b>"
            )

    # ========================================================
    # BUTTON CALLBACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^catbox_upload$"
        )
    )
    async def catbox_callback(
        client,
        callback_query
    ):

        status = callback_query.message

        files = getattr(
            client,
            "_catbox_files",
            {}
        )

        session = files.get(
            status.id
        )

        # ----------------------------------------------------
        # SESSION CHECK
        # ----------------------------------------------------

        if not session:

            await callback_query.answer(
                "❌ Image session expired.",
                show_alert=True
            )

            try:

                await status.edit_text(
                    "❌ <b>Image session expired.</b>\n\n"
                    "Use <code>/telegraph</code> again."
                )

            except Exception:

                pass

            return

        # ----------------------------------------------------
        # USER CHECK
        # ----------------------------------------------------

        if (
            callback_query.from_user.id
            != session.get("user_id")
        ):

            await callback_query.answer(
                "❌ This image belongs to another user.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # FILE
        # ----------------------------------------------------

        file_path = session.get(
            "file_path"
        )

        if (
            not file_path
            or
            not os.path.exists(file_path)
        ):

            files.pop(
                status.id,
                None
            )

            await callback_query.answer(
                "❌ Image file no longer exists.",
                show_alert=True
            )

            try:

                await status.edit_text(
                    "❌ <b>Image file no longer exists.</b>\n\n"
                    "Use <code>/telegraph</code> again."
                )

            except Exception:

                pass

            return

        await callback_query.answer(
            "Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Cᴀᴛʙᴏx"
        )

        try:

            await status.edit_text(
                "⏳ <b>Uᴘʟᴏᴀᴅɪɴɢ Tᴏ Cᴀᴛʙᴏx...</b>"
            )

            # ------------------------------------------------
            # CATBOX UPLOAD
            # ------------------------------------------------

            url = await upload_to_catbox(
                file_path
            )

            if url:

                await status.edit_text(
                    "<b>Lɪɴᴋ Gᴇɴᴇʀᴀᴛᴇᴅ</b>\n\n"
                    f"›› <code>{url}</code>",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "• Oᴘᴇɴ Lɪɴᴋ •",
                                    url=url
                                )
                            ]
                        ]
                    )
                )

            else:

                await status.edit_text(
                    "❌ <b>Catbox upload failed.</b>"
                )

        except Exception as e:

            logging.exception(
                "Catbox callback upload error: %s",
                e
            )

            try:

                await status.edit_text(
                    "❌ <b>Catbox upload failed.</b>"
                )

            except Exception:

                pass

        finally:

            # ------------------------------------------------
            # CLEANUP
            # ------------------------------------------------

            try:

                if os.path.exists(file_path):

                    os.remove(
                        file_path
                    )

            except Exception as e:

                logging.warning(
                    "Failed to remove Catbox file: %s",
                    e
                )

            files.pop(
                status.id,
                None
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity
# Support : @Coders_Grp
# ------------------------ #