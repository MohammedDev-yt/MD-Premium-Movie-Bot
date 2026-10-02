# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import asyncio
from datetime import datetime
from config import PREMIUM_PLANS

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

from database import (
    get_user,
    create_user,
    get_token_balance,
    claim_daily_tokens,
    redeem_tokens_for_premium
)

from premium import (
    format_plans,
    get_plan_by_amount
)

from utils.buttons import (
    premium_buttons
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# TOKEN BUTTONS
# ============================================================

def token_buttons():

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "• Dᴀɪʟʏ Cʟᴀɪᴍ •",
                    callback_data="token_daily"
                )
            ],
            [
                InlineKeyboardButton(
                    "• Pʀᴇᴍɪᴜᴍ •",
                    callback_data="token_premium"
                ),
                InlineKeyboardButton(
                    "• Cʟᴏѕᴇ •",
                    callback_data="token_close"
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
# TOKEN PREMIUM REDEEM BUTTONS
# ============================================================

def token_redeem_buttons():

    buttons = []

    for amount, plan in PREMIUM_PLANS.items():

        requests = plan.get(
            "requests",
            0
        )

        name = plan.get(
            "name",
            "Premium"
        )

        buttons.append(
            [
                InlineKeyboardButton(
                    f"🎟 {amount} Tᴏᴋᴇɴs → {requests} Rᴇǫᴜᴇsᴛs",
                    callback_data=f"token_redeem_{amount}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "• Bᴀᴄᴋ •",
                callback_data="token_back"
            ),
            InlineKeyboardButton(
                "• Cʟᴏѕᴇ •",
                callback_data="token_close"
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# TOKEN PANEL TEXT
# ============================================================

def build_token_text(
    first_name,
    user_id,
    balance,
    is_premium
):

    status = (
        "Pʀᴇᴍɪᴜᴍ Uѕᴇʀ"
        if is_premium
        else
        "Fʀᴇᴇ Uѕᴇʀ"
    )

    return (
        "🔘 <b>Iᴄʜɪɢᴏ Pʀᴇᴍɪᴜᴍ Mᴏᴠɪᴇ Bᴏᴛ</b> ❞\n\n"

        f"◉ <b>Uѕᴇʀ:</b> "
        f"{first_name}\n"

        f"◉ <b>Bᴀʟᴀɴᴄᴇ:</b> "
        f"<b>{balance} Tᴏᴋᴇɴѕ</b>\n"

        f"◉ <b>Sᴛᴀᴛᴜѕ:</b> "
        f"<b>{status}</b>\n\n"

        "⌛ <b>Hᴏᴡ ᴛᴏ Eᴀʀɴ?</b>\n"

        "• Cʟᴀɪᴍ ʏᴏᴜʀ <b>Dᴀɪʟʏ Rᴇᴡᴀʀᴅ</b> below!\n"
        "• Eᴀʀɴ <b>𝟻𝟶 Tᴏᴋᴇɴs</b> ᴇᴠᴇʀʏ ᴅᴀʏ.\n"
        "• Usᴇ Tᴏᴋᴇɴs Tᴏ Uɴʟᴏᴄᴋ Pʀᴇᴍɪᴜᴍ.\n\n"

        "• <b>100 Tᴏᴋᴇɴѕ</b> = "
        "<b>Sᴛᴀʀᴛᴇʀ Pʀᴇᴍɪᴜᴍ</b>\n"

        "• Sᴛᴀʀᴛᴇʀ Pʀᴇᴍɪᴜᴍ Pʟᴀɴ "
        "<b>ɢɪᴠᴇs 𝟸𝟶 ᴍᴏᴠɪᴇs ʀᴇǫᴜᴇsᴛs</b>."
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER TOKEN HANDLERS
# ============================================================

def register_token_handlers(app):

    @app.on_message(
        filters.command(
            [
                "tokens",
                "token"
            ]
        )
        & filters.private
    )
    async def tokens_command(
        client,
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

        # ----------------------------------------------------
        # GET / CREATE USER
        # ----------------------------------------------------

        user = await get_user(
            user_id
        )

        if not user:

            user = await create_user(
                user_id=user_id,
                first_name=first_name,
                username=username
            )

        # ----------------------------------------------------
        # TOKEN BALANCE
        # ----------------------------------------------------

        balance = await get_token_balance(
            user_id
        )

        is_premium = bool(
            user.get(
                "premium",
                False
            )
        )

        # ----------------------------------------------------
        # SEND TOKEN PANEL
        # ----------------------------------------------------

        await message.reply_text(
            build_token_text(
                first_name,
                user_id,
                balance,
                is_premium
            ),
            reply_markup=token_buttons()
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
    # -------------------
    # /gentoken 
    # -------------------
    @app.on_message(
        filters.command("gentoken")
        & filters.private
    )
    async def gentoken_command(
        client,
        message
    ):

        user_id = message.from_user.id

        # ----------------------------------------------------
        # GET / CREATE USER
        # ----------------------------------------------------

        user = await get_user(
            user_id
        )

        if not user:

            user = await create_user(
                user_id=user_id,
                first_name=(
                    message.from_user.first_name
                    or "User"
                ),
                username=(
                    message.from_user.username
                    or ""
                )
            )

        now = datetime.utcnow()

        today = datetime(
            now.year,
            now.month,
            now.day
        )

        last_claim = user.get(
            "last_token_claim"
        )

        if last_claim:

            # ------------------------------------------------
            # ALREADY CLAIMED
            # ------------------------------------------------

            if last_claim >= today:

                await message.reply_text(
                    "❌ ʜᴀ, ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ "
                    "ʏᴏᴜʀ ғʀᴇᴇ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ! ʏᴏᴜ'ʀᴇ ᴀᴛ "
                    "ᴛʜᴇ ᴍᴇʀᴄʏ... ᴛʀʏ ᴀɢᴀɪɴ ᴛᴏᴍᴏʀʀᴏᴡ... 🙃."
                )

                return

        # ----------------------------------------------------
        # PREVIOUS BALANCE
        # ----------------------------------------------------

        previous_tokens = await get_token_balance(
            user_id
        )

        # ----------------------------------------------------
        # ANIMATION
        # ----------------------------------------------------

        animation = await message.reply_text(
            "⚡️"
        )

        await asyncio.sleep(0.5)

        await animation.edit_text(
            "🎊"
        )

        await asyncio.sleep(0.5)

        await animation.edit_text(
            "›› ᴀᴅᴅɪɴɢ..."
        )

        await asyncio.sleep(0.5)

        # ----------------------------------------------------
        # CLAIM
        # ----------------------------------------------------

        result = await claim_daily_tokens(
            user_id
        )

        if result.get(
            "reason"
        ) == "already_claimed":

            balance = result.get(
                "tokens",
                previous_tokens
            )

            try:

                await animation.delete()

            except Exception:

                pass

            await message.reply_text(
                "❌ ʜᴀ, ʏᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ "
                "ʏᴏᴜʀ ғʀᴇᴇ ᴛᴏᴋᴇɴs ᴛᴏᴅᴀʏ! ʏᴏᴜ'ʀᴇ ᴀᴛ "
                "ᴛʜᴇ ᴍᴇʀᴄʏ... ᴛʀʏ ᴀɢᴀɪɴ ᴛᴏᴍᴏʀʀᴏᴡ... 🙃."
            )

            return

        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        if not result.get(
            "success"
        ):

            try:

                await animation.delete()

            except Exception:

                pass

            await message.reply_text(
                "❌ <b>Fᴀɪʟᴇᴅ ᴛᴏ ᴄʟᴀɪᴍ ᴛᴏᴋᴇɴs.</b>"
            )

            return

        # ----------------------------------------------------
        # NEW BALANCE
        # ----------------------------------------------------

        total_tokens = result.get(
            "tokens",
            previous_tokens
        )

        new_tokens = (
            total_tokens
            - previous_tokens
        )

        # ----------------------------------------------------
        # DELETE ANIMATION
        # ----------------------------------------------------

        try:

            await animation.delete()

        except Exception:

            pass

        # ----------------------------------------------------
        # SUCCESS MESSAGE
        # ----------------------------------------------------

        await message.reply_text(

            "✦ <b>𝗖𝗥𝗘𝗗𝗜𝗧𝗦 𝗖𝗟𝗔𝗜𝗠𝗘𝗗!</b>\n\n"

            f"◍ ᴘʀᴇᴠ ᴛᴏᴋᴇɴs: {previous_tokens}\n"
            f"◍ ɴᴇᴡ ᴛᴏᴋᴇɴs ᴀᴅᴅᴇᴅ: {new_tokens}\n"
            f"◍ ᴛᴏᴛᴀʟ ᴛᴏᴋᴇɴs: {total_tokens}\n\n"

            "⧗ ᴜsᴇ /token ᴛᴏ ᴄʜᴇᴄᴋ "
            "ʏᴏᴜʀ ᴅᴀɪʟʏ ᴛᴏᴋᴇɴ ʙᴀʟᴀɴᴄᴇ.\n"

            "≡ ᴜsᴇ /premium ᴛᴏ ᴜᴘɢʀᴀᴅᴇ "
            "ғᴏʀ ᴜɴʟɪᴍɪᴛᴇᴅ movie search"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # DAILY CLAIM BUTTON
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^token_daily$"
        )
    )
    async def token_daily_callback(
        client,
        callback
    ):

        if callback.message.chat.id != callback.from_user.id:

            await callback.answer(
                "❌ This can only be used in Bot PM.",
                show_alert=True
            )

            return

        user_id = callback.from_user.id

        result = await claim_daily_tokens(
            user_id
        )

        # ----------------------------------------------------
        # ALREADY CLAIMED
        # ----------------------------------------------------

        if result.get(
            "reason"
        ) == "already_claimed":

            balance = result.get(
                "tokens",
                0
            )

            await callback.answer(
                f"🎁 Yᴏᴜ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴄʟᴀɪᴍᴇᴅ ᴛᴏᴅᴀʏ's ʀᴇᴡᴀʀᴅ.\n"
                f"Cᴏᴍᴇ ʙᴀᴄᴋ ᴛᴏᴍᴏʀʀᴏᴡ!\n\n"
                f"Bᴀʟᴀɴᴄᴇ: {balance} tokens",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        if not result.get(
            "success"
        ):

            await callback.answer(
                "❌ Failed to claim tokens.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # NEW BALANCE
        # ----------------------------------------------------

        balance = result.get(
            "tokens",
            0
        )

        user = await get_user(
            user_id
        )

        first_name = (
            callback.from_user.first_name
            or "User"
        )

        is_premium = bool(
            user.get(
                "premium",
                False
            )
        ) if user else False

        # ----------------------------------------------------
        # UPDATE PANEL
        # ----------------------------------------------------

        await callback.message.edit_text(
            build_token_text(
                first_name,
                user_id,
                balance,
                is_premium
            ),
            reply_markup=token_buttons()
        )

        await callback.answer(
            "🎉 +50 Tᴏᴋᴇɴs Aᴅᴅᴇᴅ!",
            show_alert=True
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # PREMIUM BUTTON
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^token_premium$"
        )
    )
    async def token_premium_callback(
        client,
        callback
    ):

        if callback.message.chat.id != callback.from_user.id:

            await callback.answer(
                "❌ This can only be used in Bot PM.",
                show_alert=True
            )

            return

        await callback.answer()

        text = (
            " <b>Pʀᴇᴍɪᴜᴍ Wɪᴛʜ Tᴏᴋᴇɴs</b>\n\n"

            "<b>Usᴇ Yᴏᴜʀ Tᴏᴋᴇɴs Tᴏ Aᴄᴛɪᴠᴀᴛᴇ "
            "Aɴʏ Aᴠᴀɪʟᴀʙʟᴇ Pʀᴇᴍɪᴜᴍ Pʟᴀɴ.</b>\n\n"

            "🎟 <b><i>1 Token = ₹1 plan value</i></b>\n\n"

            "<b>›› Sᴇʟᴇᴄᴛ Tʜᴇ Pʟᴀɴ Yᴏᴜ Wᴀɴᴛ Bᴇʟᴏᴡ</b>"
        )

        await callback.message.edit_text(
            text,
            reply_markup=token_redeem_buttons()
        )

        await callback.answer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # REDEEM 100 TOKENS
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^token_redeem_\d+$"
        )
    )
    async def token_redeem_callback(
        client,
        callback
    ):

        if callback.message.chat.id != callback.from_user.id:

            await callback.answer(
                "❌ This can only be used in Bot PM.",
                show_alert=True
            )

            return

        await callback.answer()

        user_id = callback.from_user.id

        try:

            amount = int(
                callback.data.split("_")[-1]
            )

        except (ValueError, IndexError):

            await callback.answer(
                "❌ Invalid Premium plan.",
                show_alert=True
            )

            return

        plan = get_plan_by_amount(
            amount
        )

        if not plan:

            await callback.answer(
                "‼️ This Premium plan does not exist.",
                show_alert=True
            )

            return

        plan_name = plan.get(
            "name",
            "Premium"
        )

        requests = plan.get(
            "requests",
            0
        )

        result = await redeem_tokens_for_premium(
            user_id,
            amount,
            plan_name,
            requests
        )

        # ----------------------------------------------------
        # NOT ENOUGH TOKENS
        # ----------------------------------------------------

        if result.get(
            "reason"
        ) == "insufficient_tokens":

            balance = result.get(
                "tokens",
                0
            )

            await callback.answer(
                f"🧐 ʏᴏᴜ ɴᴇᴇᴅ {amount} ᴛᴏᴋᴇɴs!.\n"
                f"Current balance: {balance} ᴛᴏᴋᴇɴs",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        if not result.get(
            "success"
        ):

            await callback.answer(
                "❌ Failed to redeem tokens.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        balance = result.get(
            "tokens",
            0
        )

        await callback.message.edit_text(

            "🎉 <b>Pʀᴇᴍɪᴜᴍ Aᴄᴛɪᴠᴀᴛᴇᴅ!</b>\n\n"

            f"<b>›› Pʟᴀɴ:</b> {plan_name}\n"
            f"<b>›› Tᴏᴋᴇɴs Usᴇᴅ:</b> {amount}\n"
            f"<b>›› Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛs:</b> {requests}\n"
            f"<b>›› Rᴇᴍᴀɪɴɪɴɢ Tᴏᴋᴇɴs:</b> {balance}\n\n"

            f"<i> Yᴏᴜʀ </i><b>{plan_name}</b> <i> Pʟᴀɴ Is Nᴏᴡ Aᴄᴛɪᴠᴇ</i>\n"
            f"<i>Yᴏᴜ ᴄᴀɴ ɴᴏᴡ ᴜsᴇ ʏᴏᴜʀ</i> <b>{requests}</b> <i>Mᴏᴠɪᴇ Rᴇǫᴜᴇsᴛs</i>",

            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "• Pʀᴇᴍɪᴜᴍ Pʟᴀɴѕ •",
                            callback_data="token_premium"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "• Cʟᴏѕᴇ •",
                            callback_data="token_close"
                        )
                    ]
                ]
            )
        )

        await callback.answer(
            f"🎉 {amount} Tᴏᴋᴇɴs Rᴇᴅᴇᴇᴍᴇᴅ!",
            show_alert=True
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # BACK TO TOKEN PANEL
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^token_back$"
        )
    )
    async def token_back_callback(
        client,
        callback
    ):

        if callback.message.chat.id != callback.from_user.id:

            await callback.answer(
                "❌ This can only be used in Bot PM.",
                show_alert=True
            )

            return

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

        balance = await get_token_balance(
            user_id
        )

        is_premium = bool(
            user.get(
                "premium",
                False
            )
        )

        await callback.message.edit_text(
            build_token_text(
                callback.from_user.first_name
                or "User",
                user_id,
                balance,
                is_premium
            ),
            reply_markup=token_buttons()
        )

        await callback.answer()

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
            r"^token_close$"
        )
    )
    async def token_close_callback(
        client,
        callback
    ):

        if callback.message.chat.id != callback.from_user.id:

            await callback.answer(
                "❌ This can only be used in Bot PM.",
                show_alert=True
            )

            return

        try:

            await callback.message.delete()

        except Exception:

            pass

        await callback.answer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
