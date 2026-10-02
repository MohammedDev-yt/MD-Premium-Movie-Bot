# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import logging
import secrets
import string

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram import filters
from config import OWNER_ID

from database import (
    create_redeem_code,
    get_redeem_codes,
    ban_user,
    unban_user,
    get_banned_users,
    set_maintenance,
    is_maintenance_enabled,
)

logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# OWNER CHECK
# ============================================================

def is_owner(user_id):
    return user_id == OWNER_ID


owner_only = filters.create(
    lambda _, __, message: (
        message.from_user is not None
        and is_owner(message.from_user.id)
    )
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# GENERATE CODE
# ============================================================

def generate_code():

    alphabet = string.ascii_uppercase + string.digits

    part1 = "".join(
        secrets.choice(alphabet)
        for _ in range(4)
    )

    part2 = "".join(
        secrets.choice(alphabet)
        for _ in range(4)
    )

    return f"PMB-{part1}-{part2}"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER OWNER HANDLERS
# ============================================================

def register_owner_handlers(app):

    # --------------------------------------------------------
    # /generatecode
    # --------------------------------------------------------

    @app.on_message(
        filters.command("generatecode") & owner_only
    )
    async def generatecode_handler(client, message):

        if len(message.command) < 2:

            await message.reply_text(
                "❌ <b>Usage</b>\n\n"
                "<code>/generatecode AMOUNT</code>\n\n"
                "Example:\n"
                "<code>/generatecode 20</code>"
            )

            return

        try:
            amount = int(message.command[1])

        except ValueError:

            await message.reply_text(
                "❌ Amount must be a number."
            )

            return

        if amount <= 0:

            await message.reply_text(
                "❌ Amount must be greater than 0."
            )

            return

        # Generate a unique code
        for _ in range(10):

            code = generate_code()

            created = await create_redeem_code(
                code=code,
                amount=amount,
                created_by=message.from_user.id
            )

            if created:
                break

        else:

            await message.reply_text(
                "❌ Could not generate a unique code.\n"
                "Please try again."
            )

            return

        await message.reply_text(
            "🎟️ <b>Premium Code Generated</b>\n\n"
            f"<b>›› Code:</b> <code>{code}</code>\n"
            f"<b>›› Amount: ₹{amount}</b>\n"
            "<b>››🟢 Status: Unused</b>\n\n"
            "<b>Give this code to the customer.</b>"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # /codes
    # --------------------------------------------------------

    @app.on_message(
        filters.command("codes") & owner_only
    )
    async def codes_handler(client, message):

        codes = await get_redeem_codes()

        if not codes:

            await message.reply_text(
                "🎟️ <b>Redeem Codes</b>\n\n"
                "No codes have been generated yet."
            )

            return

        lines = [
            "🎟️ <b>Premium Redeem Codes</b>",
            ""
        ]

        for index, item in enumerate(
            codes,
            start=1
        ):

            code = item.get(
                "code",
                "UNKNOWN"
            )

            amount = item.get(
                "amount",
                0
            )

            used = item.get(
                "used",
                False
            )

            if used:

                status = "🔴 Used"

            else:

                status = "🟢 Unused"

            lines.append(
                f"{index}. <code>{code}</code>"
            )

            lines.append(
                f"   💰 ₹{amount} | {status}"
            )

            if used and item.get("used_by"):

                lines.append(
                    "   <b>››Used by:</b> "
                    f"<code>{item['used_by']}</code>"
                )

            lines.append("")

        text = "\n".join(lines)

        # Telegram message limit
        if len(text) > 3900:

            for i in range(
                0,
                len(text),
                3900
            ):

                await message.reply_text(
                    text[i:i + 3900]
                )

        else:

            await message.reply_text(text)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # /ban
    # --------------------------------------------------------

    @app.on_message(
        filters.command("ban") & owner_only
    )
    async def ban_handler(client, message):

        if len(message.command) < 2:

            await message.reply_text(
                "With reason:\n"
                "<code>/ban USER_ID reason</code>"
            )

            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ Invalid user ID."
            )

            return

        if user_id == OWNER_ID:

            await message.reply_text(
                "<b>Go To Hell, Iam The Owner</b>"
            )

            return

        reason = ""

        if len(message.command) > 2:

            reason = " ".join(
                message.command[2:]
            )

        success = await ban_user(
            user_id=user_id,
            banned_by=message.from_user.id,
            reason=reason
        )

        if not success:

            await message.reply_text(
                "❌ Failed to ban this user."
            )

            return

        text = (
            "🚫 <b>User Banned</b>\n\n"
            f"<b> ›› User ID:</b> <code>{user_id}</code>\n"
        )

        if reason:

            text += (
                f"<b>›› 📝 Reason: {reason}</b>\n"
            )

        text += (
            f"<b>›› Banned by: </b> "
            f"<code>{message.from_user.id}</code>"
        )

        await message.reply_text(text)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # /unban
    # --------------------------------------------------------

    @app.on_message(
        filters.command("unban") & owner_only
    )
    async def unban_handler(client, message):

        if len(message.command) < 2:

            await message.reply_text(
                "<code>/unban USER_ID</code>"
            )

            return

        try:

            user_id = int(
                message.command[1]
            )

        except ValueError:

            await message.reply_text(
                "❌ Invalid user ID."
            )

            return

        success = await unban_user(
            user_id
        )

        if not success:

            await message.reply_text(
                "<b> This user is not currently banned</b>."
            )

            return

        await message.reply_text(
            "✅ <b>User Unbanned</b>\n\n"
            f"<b>››  User ID:</b> <code>{user_id}</code>"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # /banlist
    # --------------------------------------------------------

    @app.on_message(
        filters.command("banlist") & owner_only
    )
    async def banlist_handler(client, message):

        banned_users = await get_banned_users()

        if not banned_users:

            await message.reply_text(
                "🚫 <b>Ban List</b>\n\n"
                "<b>No users are currently banned</b>."
            )

            return

        lines = [
            "🚫 <b>Banned Users</b>",
            ""
        ]

        for index, item in enumerate(
            banned_users,
            start=1
        ):

            user_id = item.get(
                "user_id",
                "Unknown"
            )

            reason = item.get(
                "reason",
                ""
            )

            lines.append(
                f"{index}. <code>{user_id}</code>"
            )

            if reason:

                lines.append(
                    f"   ›› {reason}"
                )

            lines.append("")

        text = "\n".join(lines)

        if len(text) > 3900:

            for i in range(
                0,
                len(text),
                3900
            ):

                await message.reply_text(
                    text[i:i + 3900]
                )

        else:

            await message.reply_text(text)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # /maintenance
    # --------------------------------------------------------

    @app.on_message(
        filters.command("maintenance") & owner_only
    )
    async def maintenance_handler(client, message):

        # /maintenance
        if len(message.command) < 2:

            status = await is_maintenance_enabled()

            if status:

                await message.reply_text(
                    "🔧 <b>Maintenance Mode</b>\n\n"
                    "<b>›› 🟢 Status: ON</b>\n\n"
                    "<b>›› Use:</b>\n"
                    "<code>/maintenance off</code>"
                )

            else:

                await message.reply_text(
                    "🔧 <b>Maintenance Mode</b>\n\n"
                    "<b>›› 🔴 Status: OFF</b>\n\n"
                    "<b>›› Use:\n"
                    "<code>/maintenance on</code>"
                )

            return

        action = message.command[1].lower()

        # /maintenance on
        if action == "on":

            await set_maintenance(True)

            await message.reply_text(
                "🔧 <b>Maintenance Mode Enabled</b>\n\n"
                "<b>Normal users can no longer use the bot.</b>"
            )

        # /maintenance off
        elif action == "off":

            await set_maintenance(False)

            await message.reply_text(
                "✅ <b>Maintenance Mode Disabled</b>\n\n"
                "<b>Users can use the bot again.</b>"
            )

        else:

            await message.reply_text(
                "<b>›› Use:</b>\n"
                "<code>/maintenance on</code>\n"
                "<code>/maintenance off</code>"
            )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #