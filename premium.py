# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from config import PREMIUM_PLANS, FREE_REQUESTS

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_plan_by_amount(amount):
    """
    Return the Premium plan for a given price.

    Example:
        20 -> Basic plan
    """

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        return None

    return PREMIUM_PLANS.get(amount)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_all_plans():
    """
    Return all configured Premium plans.
    """

    return PREMIUM_PLANS

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def can_use_movie(user):
    """
    Check whether the user has at least one request left.
    """

    if not user:
        return False

    remaining = user.get(
        "remaining_requests",
        0
    )

    try:
        remaining = int(remaining)
    except (TypeError, ValueError):
        return False

    return remaining > 0

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def is_premium(user):
    """
    Return True if the user currently has Premium.
    """

    if not user:
        return False

    return bool(
        user.get(
            "premium",
            False
        )
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_remaining_requests(user):
    """
    Return the user's remaining request count.
    """

    if not user:
        return 0

    try:
        return max(
            0,
            int(
                user.get(
                    "remaining_requests",
                    0
                )
            )
        )

    except (TypeError, ValueError):
        return 0

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def format_plans():

    lines = [
        "💎 <b>Premium Plans</b>",
        "",
        "Choose a plan according to your needs:",
        ""
    ]

    for amount, plan in PREMIUM_PLANS.items():

        name = plan.get(
            "name",
            "Premium"
        )

        requests = plan.get(
            "requests",
            0
        )

        lines.append(
            f"💰 <b>₹{amount}</b>"
        )

        lines.append(
            f"📦 {name}"
        )

        lines.append(
            f"🎬 {requests} movie requests"
        )

        lines.append("")

    lines.extend(
        [
            "━━━━━━━━━━━━━━━━━━",
            "",
            "💳 <b>Activation</b>",
            "",
            "1️⃣ Choose a plan.",
            "2️⃣ Pay the owner.",
            "3️⃣ Send your Telegram ID to the owner.",
            "4️⃣ The owner activates your plan.",
            "",
            "After activation, your request balance "
            "will be updated automatically."
        ]
    )

    return "\n".join(lines)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_user_plan_text(user):

    if not user:

        return (
            "❌ User information not found."
        )

    premium = is_premium(
        user
    )

    remaining = get_remaining_requests(
        user
    )

    total_used = user.get(
        "total_requests_used",
        0
    )

    if premium:

        plan = user.get(
            "plan",
            "Premium"
        )

        amount = user.get(
            "paid_amount",
            0
        )

        total_plan_requests = user.get(
            "premium_requests",
            0
        )

        return (
            "💎 <b>Your Premium Account</b>\n\n"

            f"📦 Plan: <b>{plan}</b>\n"
            f"💰 Paid: <b>₹{amount}</b>\n"
            f"🎬 Plan requests: "
            f"<b>{total_plan_requests}</b>\n"
            f"🎟 Remaining: "
            f"<b>{remaining}</b>\n"
            f"📊 Requests used: "
            f"<b>{total_used}</b>\n\n"

            "✅ Premium is active."
        )

    return (
        "👤 <b>Your Account</b>\n\n"

        "🆓 Plan: <b>Free</b>\n"
        f"🎟 Remaining free requests: "
        f"<b>{remaining}</b>\n"
        f"📊 Requests used: "
        f"<b>{total_used}</b>\n\n"

        "💎 Upgrade to Premium for more "
        "movie requests."
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_plan_summary(amount):

    plan = get_plan_by_amount(
        amount
    )

    if not plan:
        return None

    return {
        "amount": int(amount),

        "name": plan.get(
            "name",
            "Premium"
        ),

        "requests": int(
            plan.get(
                "requests",
                0
            )
        )
    }

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_free_plan_info():

    return {
        "name": "Free",
        "amount": 0,
        "requests": FREE_REQUESTS
    }

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
