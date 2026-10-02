# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import asyncio
import logging
from datetime import datetime, timezone

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from pyrogram import Client, enums
from pyrogram.errors import FloodWait, RPCError

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from config import (
    API_ID,
    API_HASH,
    BOT_TOKEN,
    DATABASE_CHANNEL_ID,
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from database import (
    add_media,
    get_indexer_state,
    update_indexer_state,
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from utils.helpers import (
    is_media_message,
    get_original_filename,
    get_message_title,
    get_search_key,
    human_size,
    extract_media_metadata,
)

logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

indexer_client = Client(
    "indexer_session",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

def get_media_information(message):
    """
    Extract all required information from a Telegram media
    message before storing it in MongoDB.

    Metadata extracted:
        - language
        - year
        - season
        - episode
    """

    if not message:
        return None

    if not is_media_message(message):
        return None

    file_name = get_original_filename(message)

    file_size = 0
    mime_type = None
    media_type = None

    if message.document:
        file_size = message.document.file_size or 0
        mime_type = message.document.mime_type
        media_type = "document"

    elif message.video:
        file_size = message.video.file_size or 0
        mime_type = message.video.mime_type
        media_type = "video"

    elif message.audio:
        file_size = message.audio.file_size or 0
        mime_type = message.audio.mime_type
        media_type = "audio"

    elif message.animation:
        file_size = message.animation.file_size or 0
        mime_type = message.animation.mime_type
        media_type = "animation"

    title = get_message_title(message)

    caption = message.caption or ""

    metadata_source = ""

    if file_name:
        metadata_source += f" {file_name}"

    if caption:
        metadata_source += f" {caption}"

    metadata = extract_media_metadata(
        metadata_source
    )

    language = metadata.get("language")
    year = metadata.get("year")
    season = metadata.get("season")
    episode = metadata.get("episode")
    search_key = get_search_key(
        f"{title} {file_name or ''} {caption}"
    )

    message_date = message.date

    if message_date is None:
        message_date = datetime.now(timezone.utc)

    media_data = {
        # Telegram information 
        "channel_id": message.chat.id,
        "message_id": message.id,
        "title": title,
        "title_key": get_search_key(title),
        "search_key": search_key,
        "file_name": file_name,
        "file_size": file_size,
        "file_size_text": human_size(file_size),
        "mime_type": mime_type,
        "media_type": media_type,
        "caption": caption,
        "language": language,
        "year": year,
        "season": season,
        "episode": episode,
        "date": message_date,
        "indexed_at": datetime.now(timezone.utc),
    }

    logger.info(
        "Extracted metadata | message_id=%s | title=%s | "
        "language=%s | year=%s | season=%s | episode=%s",
        message.id,
        title,
        language,
        year,
        season,
        episode,
    )

    return media_data

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def index_message(message):
    """
    Index one Telegram message into MongoDB.
    """

    try:

        if not is_media_message(message):
            return False

        media_data = get_media_information(message)

        if not media_data:
            return False

        result = await add_media(media_data)

        logger.info(
            "Indexed message: %s | title=%s | language=%s | "
            "year=%s | season=%s | episode=%s",
            message.id,
            media_data.get("title"),
            media_data.get("language"),
            media_data.get("year"),
            media_data.get("season"),
            media_data.get("episode"),
        )

        return result

    except FloodWait as e:

        logger.warning(
            "FloodWait: sleeping for %s seconds",
            e.value
        )

        await asyncio.sleep(e.value)

        return False

    except RPCError as e:

        logger.error(
            "Telegram RPC error while indexing %s: %s",
            getattr(message, "id", None),
            e,
        )

        return False

    except Exception as e:

        logger.exception(
            "Error indexing message %s: %s",
            getattr(message, "id", None),
            e,
        )

        return False

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def handle_database_post(client, message):
    """
    Handle a new post from the database channel.

    This function is also imported by bot.py, so keep this
    exact function name.
    """

    try:

        if not message:
            return

        if not message.chat:
            return

        if message.chat.id != DATABASE_CHANNEL_ID:
            return

        if not is_media_message(message):
            return

        success = await index_message(message)

        if success:
            logger.info(
                "Database post indexed successfully: %s",
                message.id
            )
        else:
            logger.warning(
                "Database post was not indexed: %s",
                message.id
            )

    except FloodWait as e:

        logger.warning(
            "FloodWait while processing database post: %s seconds",
            e.value
        )

        await asyncio.sleep(e.value)

    except RPCError as e:

        logger.error(
            "Telegram RPC error while processing database post %s: %s",
            getattr(message, "id", None),
            e,
        )

    except Exception as e:

        logger.exception(
            "Error processing database post %s: %s",
            getattr(message, "id", None),
            e,
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

@indexer_client.on_message()
async def new_database_message(client, message):

    await handle_database_post(
        client,
        message
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def index_channel_history(
    start_message_id=None,
    end_message_id=None,
):
    """
    Index existing messages from the database channel.

    NOTE:
    Telegram bot accounts have restrictions when reading
    channel history. This function is kept for installations
    where the bot is able to access the required messages.
    """

    logger.info(
        "Starting channel history indexing..."
    )

    indexed_count = 0

    try:

        async for message in indexer_client.get_chat_history(
            DATABASE_CHANNEL_ID
        ):

            if start_message_id is not None:
                if message.id < start_message_id:
                    continue

            if end_message_id is not None:
                if message.id > end_message_id:
                    continue

            if not is_media_message(message):
                continue

            success = await index_message(message)

            if success:
                indexed_count += 1

            await asyncio.sleep(0.05)

    except FloodWait as e:

        logger.warning(
            "FloodWait during history indexing: %s seconds",
            e.value
        )

        await asyncio.sleep(e.value)

    except Exception as e:

        logger.exception(
            "History indexing failed: %s",
            e
        )

    logger.info(
        "History indexing completed. Indexed: %s",
        indexed_count
    )

    return indexed_count

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def start_indexer():

    logger.info(
        "Starting database channel indexer..."
    )

    if indexer_client.is_connected:
        logger.info(
            "Indexer is already connected."
        )
        return

    await indexer_client.start()

    logger.info(
        "Indexer connected successfully."
    )

    logger.info(
        "Database channel ID: %s",
        DATABASE_CHANNEL_ID
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def stop_indexer():

    try:

        if indexer_client.is_connected:

            await indexer_client.stop()

            logger.info(
                "Indexer stopped."
            )

    except Exception as e:

        logger.exception(
            "Error stopping indexer: %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def run_indexer():

    """
    Convenience function for manually starting the indexer.
    """

    await start_indexer()

    try:

        await asyncio.Event().wait()

    finally:

        await stop_indexer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        ),
    )

    try:

        indexer_client.run(
            start_indexer()
        )

    except KeyboardInterrupt:

        logger.info(
            "Indexer stopped by user."
        )

    except Exception as e:

        logger.exception(
            "Indexer crashed: %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
