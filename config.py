# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
DATABASE_CHANNEL_ID = int(os.getenv("DATABASE_CHANNEL_ID", "0"))

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

OWNER_ID = int(os.getenv("OWNER_ID", "0"))

ADMIN_IDS = set()

for admin_id in os.getenv("ADMIN_IDS", "").split(","):
    admin_id = admin_id.strip()

    if admin_id.isdigit():
        ADMIN_IDS.add(int(admin_id))

if OWNER_ID:
    ADMIN_IDS.add(OWNER_ID)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

STORAGE_LIMIT_MB = float(
    os.getenv(
        "STORAGE_LIMIT_MB",
        "512"
    )
)

MONGO_URI = os.getenv("MONGO_URI", "")

DB_NAME = os.getenv(
    "DB_NAME",
    "premium_movie_bot"
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

BOT_USERNAME = os.getenv(
    "BOT_USERNAME",
    ""
)

UPDATES_CHANNEL = os.getenv(
    "UPDATES_CHANNEL",
    ""
)

PORT = int(
    os.getenv("PORT", "8080")
)

FREE_REQUESTS = 500

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

PREMIUM_PLANS = {
    10: {
        "name": "Starter",
        "requests": 20
    },

    20: {
        "name": "Basic",
        "requests": 30
    },

    50: {
        "name": "Plus",
        "requests": 75
    },

    100: {
        "name": "Pro",
        "requests": 150
    },

    200: {
        "name": "Premium",
        "requests": 300
    },

    500: {
        "name": "Ultra",
        "requests": 600
    },

    1000: {
        "name": "Ultimate",
        "requests": 1000
    }
}

RESULTS_PER_PAGE = int(
    os.getenv("RESULTS_PER_PAGE", "10")
)

MAX_RESULTS = int(
    os.getenv("MAX_RESULTS", "50")
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

DELETE_AFTER = int(
    os.getenv("DELETE_AFTER", "0")
)

# Number of Telegram messages processed per indexing batch.

INDEX_BATCH_SIZE = int(
    os.getenv("INDEX_BATCH_SIZE", "100")
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO"
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
