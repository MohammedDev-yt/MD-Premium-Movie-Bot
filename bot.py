# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import asyncio
import logging
import threading

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from flask import Flask
from pyrogram import Client, filters
from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    PORT,
    LOG_LEVEL,
    DATABASE_CHANNEL_ID
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from database import (
    init_database,
    close_database
)

from handlers.font import (
    register_font_handlers
)

from handlers.start import (
    register_start_handlers
)

from handlers.premium import (
    register_premium_handlers
)

from handlers.search import (
    register_search_handlers
)

from handlers.tokens import (
    register_token_handlers
)

from handlers.admin import (
    register_admin_handlers
)

from handlers.fsub import (
    register_fsub_handlers
)

from handlers.channel import (
    register_channel_handlers
)

from handlers.group_welcome import (
    register_group_welcome_handlers
)

from handlers.access import (
    register_access_handlers
)

from handlers.owner import (
    register_owner_handlers
)

from handlers.redeem import (
    register_redeem_handlers
)

from handlers.permanent_links import (
    register_permanent_link_handlers
)

from handlers.telegraph import (
    register_telegraph_handlers
)

from handlers.share import (
    register_share_handlers
)

from handlers.system import (
    register_system_handlers
)

from indexer import (
    handle_database_post
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

logging.basicConfig(
    level=getattr(
        logging,
        LOG_LEVEL.upper(),
        logging.INFO
    ),
    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    )
)

logger = logging.getLogger(
    "premium_movie_bot"
)

web_app = Flask(
    __name__
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

@web_app.route("/")
def home():

    return "Premium Movie Bot is running."

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

@web_app.route("/health")
def health():

    return {
        "status": "ok",
        "bot": "running"
    }

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def run_web_server():

    web_app.run(
        host="0.0.0.0",
        port=PORT
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def validate_config():

    missing = []

    if not BOT_TOKEN:
        missing.append("BOT_TOKEN")

    if not API_ID:
        missing.append("API_ID")

    if not API_HASH:
        missing.append("API_HASH")

    if missing:

        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def main():

    validate_config()

    logger.info(
        "Starting Premium Movie Bot..."
    )

    await init_database()

    logger.info(
        "MongoDB initialized and Connected 🛰."
    )

    logger.info("TEST 1")

    app = Client(
        "premium_movie_bot",

        api_id=API_ID,

        api_hash=API_HASH,

        bot_token=BOT_TOKEN,

        workers=4
    )

    logger.info("TEST 2")

    @app.on_message(filters.animation)
    async def get_gif_id(client, message):
        await message.reply_text(
            f"✅ GIF FILE ID:\n\n"
            f"<code>{message.animation.file_id}</code>"
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # DATABASE CHANNEL AUTO INDEXER
    # ========================================================

    @app.on_message(
        filters.channel
        & filters.chat(DATABASE_CHANNEL_ID)
    )
    async def database_channel_post_handler(
        client,
        message
    ):

        try:

            indexed = await handle_database_post(
                client,
                message
            )

            if indexed:

                logger.info(
                    "AUTO INDEXED | "
                    "channel=%s | "
                    "message_id=%s",
                    message.chat.id,
                    message.id
                )

        except Exception as e:

            logger.exception(
                "Auto-index failed | message_id=%s | error=%s",
                message.id,
                e
            )
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # --------------------------------------------------------
    # REGISTER HANDLERS
    # --------------------------------------------------------

    register_fsub_handlers(app)

    logger.info("TEST 3")

    register_access_handlers(app)

    logger.info("TEST 4")

    register_owner_handlers(app)

    logger.info("TEST 5")
    
    register_redeem_handlers(app)

    logger.info("TEST 6")

    register_permanent_link_handlers(app)

    logger.info("PERMANENT LINKS HANDLERS REGISTERED , Test 7")

    register_telegraph_handlers(app)

    logger.info("TELEGRAPH HANDLERS REGISTERED, Test 8")

    register_share_handlers(app)

    logger.info("SHARE HANDLERS REGISTERED, Test 9")

    register_system_handlers(app)

    logger.info("SYSTEM HANDLERS REGISTERED, Test 10")
    
    register_start_handlers(app)

    logger.info("TEST 11")

    register_premium_handlers(app)

    logger.info("TEST 12")

    register_search_handlers(app)

    logger.info("TEST 13")

    register_token_handlers(app)

    logger.info("TEST 14")

    register_channel_handlers(app)

    logger.info("TEST 15")

    register_group_welcome_handlers(app)
    
    logger.info("TEST 16")
    
    register_font_handlers(app)

    logger.info("TEST 17")

    register_admin_handlers(app)

    logger.info("TEST 18")

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    @app.on_message(
        filters.all,
        group=99
    )
    async def debug_update_handler(
        client,
        message
    ):

        logger.info(
            "UPDATE RECEIVED | "
            "chat_id=%s | "
            "user_id=%s | "
            "text=%r",

            message.chat.id
            if message.chat
            else None,

            message.from_user.id
            if message.from_user
            else None,

            message.text
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    logger.info("TEST 19")

    await app.start()

    logger.info(
        "Telegram client started successfully."
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    me = await app.get_me()

    logger.info(
        "Telegram bot connected."
    )

    logger.info(
        "Bot username: @%s",
        me.username
    )

    logger.info(
        "Bot ID: %s",
        me.id
    )

    logger.info(
        "CONFIG CHECK | DATABASE_CHANNEL_ID=%r",
        DATABASE_CHANNEL_ID
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    try:

        database_chat = await app.get_chat(
            DATABASE_CHANNEL_ID
        )

        logger.info(
            "DATABASE CHANNEL CONNECTED | "
            "ID=%s | TITLE=%s | USERNAME=%s",
            database_chat.id,
            database_chat.title,
            database_chat.username
        )

    except Exception as e:

        logger.exception(
            "DATABASE CHANNEL ERROR | ID=%s | ERROR=%s",
            DATABASE_CHANNEL_ID,
            e
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    try:

        await asyncio.Event().wait()

    finally:

        logger.info(
            "Stopping bot because bot is dead..Contact To Owner"
        )

        await app.stop()

        await close_database()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

if __name__ == "__main__":

    web_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    web_thread.start()

    logger.info(
        "Web server started on port %s.",
        PORT
    )

    try:

        asyncio.run(
            main()
        )

    except KeyboardInterrupt:

        logger.info(
            "Bot stopped, because bot is dead...Contact to Owner"
        )

    except Exception as e:

        logger.exception(
            "Critical startup error: %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #