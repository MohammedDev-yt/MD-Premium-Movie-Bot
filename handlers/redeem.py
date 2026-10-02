# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import logging
from premium import get_plan_by_amount
from pyrogram import filters
from database import (
    create_user,
    get_redeem_code,
    redeem_code,
    activate_premium,
)

logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def register_redeem_handlers(app):

    @app.on_message(filters.command("redeem"))
    async def redeem_handler(client, message):

        # ---------------------------------------------
        # CHECK CODE PROVIDED
        # ---------------------------------------------

        if len(message.command) < 2:

            await message.reply_text(
                "<code>/redeem CODE</code>\n\n"
                "Example:\n"
                "<code>/redeem PMB-AB12-CD34</code>"
            )

            return

        code = message.command[1].strip().upper()
        user_id = message.from_user.id

        # ---------------------------------------------
        # GET CODE
        # ---------------------------------------------

        code_data = await get_redeem_code(code)

        if not code_data:

            await message.reply_text(
                "❌ <b>Iɴᴠᴀʟɪᴅ Rᴇᴅᴇᴇᴍ Cᴏᴅᴇ</b>\n\n"
                "<b>Tʜɪs Cᴏᴅᴇ Dᴏᴇs Nᴏᴛ Exɪᴛs</b>."
            )

            return

        # ---------------------------------------------
        # CHECK IF USED
        # ---------------------------------------------

        if code_data.get("used"):

            await message.reply_text(
                "❌ <b>Cᴏᴅᴇ Aʟʀᴇᴀᴅʏ Usᴇᴅ</b>\n\n"
                "<b>Tʜɪs Cᴏᴅᴇ Hᴀs Aʟʀᴇᴀᴅʏ Bᴇᴇɴ Rᴇᴅᴇᴇᴍᴇᴅ</b>"
            )

            return

        # ---------------------------------------------
        # GET AMOUNT
        # ---------------------------------------------

        try:

            amount = int(
                code_data.get("amount")
            )

        except (TypeError, ValueError):

            await message.reply_text(
                "❌ <b>Iɴᴠᴀʟɪᴅ Cᴏᴅᴇ</b>\n\n"
                "Tʜᴇ ᴀᴍᴏᴜɴᴛ ʟɪɴᴋᴇᴅ ᴛᴏ ᴛʜɪs ᴄᴏᴅᴇ ɪs ɪɴᴠᴀʟɪᴅ."
            )

            return

        # ---------------------------------------------
        # FIND PLAN
        # ---------------------------------------------

        plan = get_plan_by_amount(
            amount
        )

        if not plan:

            await message.reply_text(
                "‼️ <b>Pʟᴀɴ Nᴏᴛ Fᴏᴜɴᴅ</b>\n\n"
                f"›› Tʜɪs Cᴏᴅᴇ Is Wᴏʀᴛʜ ₹{amount}, "
                "<b>›› Bᴜᴛ Nᴏ Pʀᴇᴍɪᴜᴍ Pʟᴀɴ Exɪᴛs Fᴏʀ Tʜɪs Aᴍᴏᴜɴᴛ</b>.\n\n"
                "<b>›› Pʟᴇᴀsᴇ Cᴏɴᴛᴀᴄᴛ Tʜᴇ Oᴡɴᴇʀ [@Mr_Mohammed_29]</b>."
            )

            return

        plan_name = plan.get(
            "name",
            "Premium"
        )

        try:

            requests = int(
                plan.get(
                    "requests",
                    0
                )
            )

        except (TypeError, ValueError):

            requests = 0

        if requests <= 0:

            await message.reply_text(
                "❌ <b>Iɴᴠᴀʟɪᴅ Pʀᴇᴍɪᴜᴍ Cᴏᴅᴇ</b>\n\n"
                "<b>›› Tʜɪs ᴘʟᴀɴ ʜᴀs ɴᴏ ᴠᴀʟɪᴅ ᴍᴏᴠɪᴇ ʀᴇǫᴜᴇsᴛs</b>"
            )

            return

        # ---------------------------------------------
        # CREATE USER IF NEEDED
        # ---------------------------------------------

        try:

            await create_user(
                user_id
            )

        except Exception as e:

            logger.warning(
                "create_user failed for %s: %s",
                user_id,
                e
            )

        # ---------------------------------------------
        # ACTIVATE PREMIUM
        # ---------------------------------------------

        try:

            activated = await activate_premium(
                user_id=user_id,
                plan_name=plan_name,
                amount=amount,
                requests=requests
            )

        except Exception as e:

            logger.error(
                "Premium activation failed: %s",
                e
            )

            await message.reply_text(
                "❌ <b>Aᴄᴛɪᴠᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ</b>\n\n"
                "<b>›› Pʟᴇᴀsᴇ Cᴏɴᴛᴀᴄᴛ Tʜᴇ Oᴡɴᴇʀ [@Mr_Mohammed_29]</b>"
            )

            return

        if not activated:

            await message.reply_text(
                "❌ <b>Aᴄᴛɪᴠᴀᴛɪᴏɴ Fᴀɪʟᴇᴅ</b>\n\n"
                "<b>›› Pʟᴇᴀsᴇ Cᴏɴᴛᴀᴄᴛ Tʜᴇ Oᴡɴᴇʀ [@Mr_Mohammed_29]</b>"
            )

            return

        # ---------------------------------------------
        # MARK CODE AS USED
        # ---------------------------------------------

        result = await redeem_code(
            code=code,
            user_id=user_id
        )

        if not result.get("success"):

            logger.error(
                "Premium activated but code could not "
                "be marked as used: %s",
                code
            )

            await message.reply_text(
                " <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"
                f"<b>›› Pʟᴀɴ: {plan_name}</b>\n"
                f"<b>›› Rᴇǫᴜᴇsᴛs : {requests}</b>\n\n"
                "<b>Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ɪs ᴀᴄᴛɪᴠᴇ.</b>\n"
                "<b>Pʟᴇᴀsᴇ ᴄᴏɴᴛᴀᴄᴛ ᴛʜᴇ ᴏᴡɴᴇʀ [@Mr_Mohammed_29] ᴀʙᴏᴜᴛ ᴛʜᴇ ᴄᴏᴅᴇ.</b>"
            )

            return

        # ---------------------------------------------
        # SUCCESS
        # ---------------------------------------------

        await message.reply_text(
            "🎉 <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n"
            f"<b>›› Pʟᴀɴ: {plan_name}</b>\n"
            f"<b>›› Aᴍᴏᴜɴᴛ: ₹{amount}</b>\n"
            f"<b>›› Rᴇǫᴜᴇsᴛs: <b>{requests}</b>\n"
            f"<b>›› Cᴏᴅᴇ: </b> <code>{code}</code>\n\n"
            "<b>›› ✅Yᴏᴜʀ Pʀᴇᴍɪᴜᴍ ᴘʟᴀɴ ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ</b>\n"
        )
        
        # ---------------------------------------------
        # REDEEM BUTTON
        # ---------------------------------------------
        @app.on_callback_query(filters.regex("^redeem$"))
        async def redeem_button_callback(client, callback_query):

            await callback_query.answer()

            await callback_query.message.edit_text(
                "<code>/redeem YOUR_CODE</code>\n\n"
                "Example:\n"
                "<code>/redeem PMB-AB12-CD34</code>"
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #