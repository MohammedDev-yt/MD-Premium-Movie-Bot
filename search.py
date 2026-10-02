# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import re
import logging

from typing import Optional

from config import RESULTS_PER_PAGE, DATABASE_CHANNEL_ID, MAX_RESULTS, FREE_REQUESTS

from pyrogram import enums

from database import (
    search_media,
    create_search_session,
    get_search_session,
    update_search_session_filters,
    get_filter_options,
    get_or_create_user,
    can_make_request,
    consume_request,
    restore_request,
)

from handlers.fsub import (
    check_all_fsubs,
    send_fsub_message,
)

from utils.buttons import file_sent_buttons

from utils.helpers import escape_html

logger = logging.getLogger(__name__)


# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def clean_query(query: str) -> str:
    if not query:
        return ""

    query = str(query).strip()

    query = re.sub(
        r"\b(19[6-9]\d|20[0-2]\d)\b",
        " ",
        query,
    )

    query = re.sub(
        r"\bS\d{1,2}\b",
        " ",
        query,
        flags=re.IGNORECASE,
    )

    query = re.sub(
        r"\bE\d{1,3}\b",
        " ",
        query,
        flags=re.IGNORECASE,
    )

    query = re.sub(
        r"\bSEASON\s*\d{1,2}\b",
        " ",
        query,
        flags=re.IGNORECASE,
    )

    query = re.sub(
        r"\bEP(?:ISODE)?\s*\d{1,3}\b",
        " ",
        query,
        flags=re.IGNORECASE,
    )

    query = re.sub(
        r"[\[\]\(\)\{\}_\-]+",
        " ",
        query,
    )

    query = re.sub(
        r"\s+",
        " ",
        query,
    )

    return query.strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def normalize_query(query: str) -> str:
    if not query:
        return ""

    query = str(query).lower().strip()

    query = re.sub(
        r"[^a-z0-9\u0900-\u097f\u0b80-\u0bff\u0c00-\u0c7f\u0d00-\u0d7f\s]",
        " ",
        query,
    )

    query = re.sub(
        r"\s+",
        " ",
        query,
    )

    return query.strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def escape_regex(text: str) -> str:
    return re.escape(text or "")

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def create_search_patterns(query: str):
    query = normalize_query(query)

    if not query:
        return []

    words = query.split()

    patterns = []

    # Exact phrase
    patterns.append(query)

    # Individual words
    for word in words:
        if word and word not in patterns:
            patterns.append(word)

    # Prefix-style patterns
    if words:
        patterns.append(" ".join(words))

    return list(dict.fromkeys(patterns))

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_title(result: dict) -> str:
    if not result:
        return "Unknown File"

    title = (
        result.get("title")
        or result.get("file_name")
        or result.get("filename")
        or result.get("name")
        or "Unknown File"
    )

    return str(title).strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_message_id(result: dict):
    if not result:
        return None

    message_id = (
        result.get("message_id")
        or result.get("telegram_message_id")
        or result.get("msg_id")
    )

    try:
        return int(message_id)
    except Exception:
        return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def normalize_filters(filters=None):
    """
    Normalizes all supported search filters.

    Supported filters:
        language
        year
        season
        episode
        quality
    """

    if not filters:
        return {}

    output = {}

    language = filters.get("language")
    year = filters.get("year")
    season = filters.get("season")
    episode = filters.get("episode")
    quality = filters.get("quality")

    if language:
        output["language"] = str(language).strip()


    if year not in (None, "", 0):
        try:
            year = int(year)

            if 1960 <= year <= 2026:
                output["year"] = year

        except Exception:
            pass

    if season not in (None, "", 0):
        try:
            season = int(season)

            if 1 <= season <= 20:
                output["season"] = season

        except Exception:
            pass

    if episode not in (None, "", 0):
        try:
            episode = int(episode)

            if 1 <= episode <= 50:
                output["episode"] = episode

        except Exception:
            pass

    if quality:
        quality = str(quality).strip()

        if quality:
            output["quality"] = quality

    return output

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def filter_label(filters=None) -> str:
    """
    Returns a readable label for active filters.
    """

    filters = normalize_filters(filters)

    parts = []

    if filters.get("language"):
        parts.append(
            str(filters["language"])
        )

    if filters.get("year"):
        parts.append(
            str(filters["year"])
        )

    if filters.get("quality"):
        parts.append(
            str(filters["quality"])
        )

    if filters.get("season"):
        parts.append(
            f"S{int(filters['season']):02d}"
        )

    if filters.get("episode"):
        parts.append(
            f"E{int(filters['episode']):02d}"
        )

    if not parts:
        return "All"

    return " • ".join(parts)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def search_movies(
    query: str,
    page: int = 0,
    filters: Optional[dict] = None,
):
    """
    Search media with optional filters.

    Supported filters:
        language
        year
        season
        episode
        quality
    """

    try:
        query = clean_query(query)

        if not query:
            return [], False

        filters = normalize_filters(
            filters
        )

        page = max(
            0,
            int(page),
        )

        per_page = int(
            RESULTS_PER_PAGE or 10
        )

        if per_page <= 0:
            per_page = 10

        skip = page * per_page

        # One extra result is requested
        # to determine whether next page exists.
        limit = per_page + 1

        results = await search_media(
            query=query,
            skip=skip,
            limit=limit,
            filters=filters,
        )

        if not results:
            return [], False

        results = list(results)

        has_next = (
            len(results) > per_page
        )

        if has_next:
            results = results[:per_page]

        return results, has_next

    except Exception:
        logger.exception(
            "search_movies failed"
        )

        return [], False

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def advanced_search(
    query: str,
    page: int = 0,
    filters: Optional[dict] = None,
):
    """
    Performs normal search first.
    If nothing is found, searches individual words.
    """

    filters = normalize_filters(
        filters
    )

    results, has_next = await search_movies(
        query=query,
        page=page,
        filters=filters,
    )

    if results:
        return results, has_next

    words = normalize_query(
        query
    ).split()

    if not words:
        return [], False

    collected = []
    seen = set()

    for word in words:

        word_results, _ = await search_movies(
            query=word,
            page=0,
            filters=filters,
        )

        for result in word_results:

            message_id = get_result_message_id(
                result
            )

            if message_id is None:
                continue

            if message_id in seen:
                continue

            seen.add(message_id)
            collected.append(result)

            if len(collected) >= MAX_RESULTS:
                break

        if len(collected) >= MAX_RESULTS:
            break

    per_page = int(
        RESULTS_PER_PAGE or 10
    )

    start = page * per_page
    end = start + per_page

    page_results = collected[
        start:end
    ]

    has_next = (
        end < len(collected)
    )

    return page_results, has_next

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def search_exact_title(
    query: str,
    filters: Optional[dict] = None,
):
    """
    Exact-title style search.
    """

    filters = normalize_filters(
        filters
    )

    results, _ = await search_movies(
        query=query,
        page=0,
        filters=filters,
    )

    normalized = normalize_query(
        query
    )

    exact = []

    for result in results:

        title = get_result_title(
            result
        )

        if normalize_query(title) == normalized:
            exact.append(result)

    return exact

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_filters(
    query: str,
    filters: Optional[dict] = None,
):
    """
    Returns only filter values that actually
    exist for the current search.

    Returns:

        languages
        years
        qualities
        seasons
        episodes
    """

    try:
        filters = normalize_filters(
            filters
        )

        return await get_filter_options(
            query=query,
            filters=filters,
        )

    except Exception:
        logger.exception(
            "get_available_filters failed"
        )

        return {
            "languages": [],
            "years": [],
            "qualities": [],
            "seasons": [],
            "episodes": [],
        }

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_languages(
    query: str,
    filters: Optional[dict] = None,
):
    options = await get_available_filters(
        query,
        filters,
    )

    return options.get(
        "languages",
        [],
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_years(
    query: str,
    filters: Optional[dict] = None,
):
    options = await get_available_filters(
        query,
        filters,
    )

    return options.get(
        "years",
        [],
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_qualities(
    query: str,
    filters: Optional[dict] = None,
):
    """
    Returns available quality values.
    """

    options = await get_available_filters(
        query,
        filters,
    )

    return options.get(
        "qualities",
        [],
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_seasons(
    query: str,
    filters: Optional[dict] = None,
):
    options = await get_available_filters(
        query,
        filters,
    )

    return options.get(
        "seasons",
        [],
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_episodes(
    query: str,
    filters: Optional[dict] = None,
):
    options = await get_available_filters(
        query,
        filters,
    )

    return options.get(
        "episodes",
        [],
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def create_filtered_search_session(
    user_id: int,
    query: str,
    filters: Optional[dict] = None,
):
    """
    Creates a search session with filters saved.
    """

    filters = normalize_filters(
        filters
    )

    return await create_search_session(
        user_id=user_id,
        query=query,
        filters=filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def set_search_filters(
    session_id: str,
    user_id: int,
    filters: Optional[dict] = None,
):
    """
    Updates filters for an existing
    search session.
    """

    filters = normalize_filters(
        filters
    )

    return await update_search_session_filters(
        session_id=session_id,
        user_id=user_id,
        filters=filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_saved_search(
    session_id: str,
    user_id: int,
):
    """
    Returns saved search session.
    """

    return await get_search_session(
        session_id=session_id,
        user_id=user_id,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def search_session(
    session_id: str,
    user_id: int,
    page: int = 0,
):
    """
    Searches using the query + filters
    stored in the session.
    """

    session = await get_search_session(
        session_id=session_id,
        user_id=user_id,
    )

    if not session:
        return [], False, None

    query = session.get(
        "query",
        "",
    )

    filters = normalize_filters(
        session.get("filters") or {}
    )

    results, has_next = await search_movies(
        query=query,
        page=page,
        filters=filters,
    )

    return (
        results,
        has_next,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def apply_language_filter(
    session_id: str,
    user_id: int,
    language: Optional[str],
):
    session = await get_search_session(
        session_id,
        user_id,
    )

    if not session:
        return False

    filters = normalize_filters(
        session.get("filters") or {}
    )

    if language:
        filters["language"] = (
            str(language).strip()
        )
    else:
        filters.pop(
            "language",
            None,
        )

    return await set_search_filters(
        session_id,
        user_id,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def apply_year_filter(
    session_id: str,
    user_id: int,
    year,
):
    session = await get_search_session(
        session_id,
        user_id,
    )

    if not session:
        return False

    filters = normalize_filters(
        session.get("filters") or {}
    )

    if year in (None, "", 0):

        filters.pop(
            "year",
            None,
        )

    else:

        try:
            year = int(year)

            if 1960 <= year <= 2026:
                filters["year"] = year

        except Exception:
            return False

    return await set_search_filters(
        session_id,
        user_id,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def apply_quality_filter(
    session_id: str,
    user_id: int,
    quality: Optional[str],
):
    """
    Applies or removes the quality filter.
    """

    session = await get_search_session(
        session_id,
        user_id,
    )

    if not session:
        return False

    filters = normalize_filters(
        session.get("filters") or {}
    )

    if quality:

        quality = str(
            quality
        ).strip()

        if quality:
            filters["quality"] = quality
        else:
            filters.pop(
                "quality",
                None,
            )

    else:

        filters.pop(
            "quality",
            None,
        )

    return await set_search_filters(
        session_id,
        user_id,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def apply_season_filter(
    session_id: str,
    user_id: int,
    season,
):
    session = await get_search_session(
        session_id,
        user_id,
    )

    if not session:
        return False

    filters = normalize_filters(
        session.get("filters") or {}
    )

    if season in (None, "", 0):

        filters.pop(
            "season",
            None,
        )

        # Episode belongs to season.
        filters.pop(
            "episode",
            None,
        )

    else:

        try:
            season = int(season)

            if 1 <= season <= 20:
                filters["season"] = season

        except Exception:
            return False

    return await set_search_filters(
        session_id,
        user_id,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def apply_episode_filter(
    session_id: str,
    user_id: int,
    episode,
):
    session = await get_search_session(
        session_id,
        user_id,
    )

    if not session:
        return False

    filters = normalize_filters(
        session.get("filters") or {}
    )

    if episode in (None, "", 0):

        filters.pop(
            "episode",
            None,
        )

    else:

        try:
            episode = int(episode)

            if 1 <= episode <= 50:
                filters["episode"] = episode

        except Exception:
            return False

    return await set_search_filters(
        session_id,
        user_id,
        filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def clear_all_filters(
    session_id: str,
    user_id: int,
):
    return await set_search_filters(
        session_id=session_id,
        user_id=user_id,
        filters={},
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def send_database_file(
    client,
    user_id: int,
    message_id: int,
):
    """
    Sends/copies the requested file from
    the database channel.

    The caption is:
        - bold
        - clickable
        - points to the Updates channel
    """

    try:

        database_chat = await client.get_chat(
            DATABASE_CHANNEL_ID
        )

        logger.info(
            "Sending database file %s to user %s",
            message_id,
            user_id,
        )

        source_message = await client.get_messages(
            database_chat.id,
            int(message_id),
        )

        if not source_message:
            raise ValueError(
                f"Database message {message_id} not found"
            )

        original_caption = (
            source_message.caption or ""
        )

        # ----------------------------------------------------
        # NO CAPTION
        # ----------------------------------------------------

        if not original_caption:

            return await client.copy_message(
                chat_id=user_id,
                from_chat_id=database_chat.id,
                message_id=int(message_id),
                reply_markup=file_sent_buttons(),
            )

        # ----------------------------------------------------
        # CLICKABLE + BOLD CAPTION
        # ----------------------------------------------------

        clickable_caption = (
            '<a href="https://t.me/Aero_Unity">'
            f"<b>{escape_html(original_caption)}</b>"
            "</a>"
        )

        sent_message = await client.copy_message(
            chat_id=user_id,
            from_chat_id=database_chat.id,
            message_id=int(message_id),
            caption=clickable_caption,
            parse_mode=enums.ParseMode.HTML,
            reply_markup=file_sent_buttons(),
        )

        return sent_message

    except Exception:

        logger.exception(
            "Failed to send database file %s to user %s",
            message_id,
            user_id,
        )

        raise

# ============================================================
# DEEP LINK: FILE
# ============================================================

async def handle_file_deep_link(
    client,
    message,
    message_id,
):
    """
    Handles:

        /start file_<message_id>

    This MUST run in private chat.

    FSub is checked here before file delivery.
    """

    try:

        if message.chat.type != "private":
            return

        user_id = message.from_user.id

        try:
            message_id = int(
                message_id
            )

        except Exception:

            await message.reply_text(
                "❌ Invalid file link."
            )

            return

        await get_or_create_user(
            user_id
        )

        # ----------------------------------------------------
        # FORCE SUBSCRIBE
        # ----------------------------------------------------

        joined = await check_all_fsubs(
            client,
            user_id,
        )

        if not joined:

            await send_fsub_message(
                client,
                message,
                deep_link=f"file_{message_id}",
            )

            return

        allowed = await can_make_request(
            user_id,
            FREE_REQUESTS,
        )

        if not allowed:

            await message.reply_text(
                "⚠️ You have reached your request limit."
            )

            return

        consumed = await consume_request(
            user_id
        )

        if not consumed:

            await message.reply_text(
                "⚠️ Unable to process your request."
            )

            return

        # ----------------------------------------------------
        # SEND FILE
        # ----------------------------------------------------

        try:

            sent_message = await send_database_file(
                client,
                user_id,
                message_id,
            )

            # ------------------------------------------------
            # AUTO DELETE AFTER 5 MINUTES
            # ------------------------------------------------

            if sent_message:

                import asyncio

                async def delete_later():

                    await asyncio.sleep(
                        300
                    )

                    try:
                        await sent_message.delete()

                    except Exception:
                        pass

                asyncio.create_task(
                    delete_later()
                )

            return sent_message

        except Exception:

            # Restore consumed request
            # if delivery fails.
            try:

                await restore_request(
                    user_id
                )

            except Exception:

                logger.exception(
                    "Failed restoring request for user %s",
                    user_id,
                )

            await message.reply_text(
                "❌ File could not be sent."
            )

    except Exception:

        logger.exception(
            "handle_file_deep_link failed"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# DEEP LINK: SEND ALL
# ============================================================

async def handle_sendall_deep_link(
    client,
    message,
    session_id,
    page=0,
):
    """
    Handles:

        /start sendall_<session_id>_<page>

    Uses the filters saved in the search session.
    """

    try:

        if message.chat.type != "private":
            return

        user_id = message.from_user.id

        try:
            page = int(page)

        except Exception:
            page = 0

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

        # ----------------------------------------------------
        # GET SESSION
        # ----------------------------------------------------

        results, has_next, filters = await search_session(
            session_id=session_id,
            user_id=user_id,
            page=page,
        )

        if not results:

            await message.reply_text(
                "❌ Search results expired or no files were found."
            )

            return

        await get_or_create_user(
            user_id
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

        # ----------------------------------------------------
        # FORCE SUBSCRIBE
        # ----------------------------------------------------

        joined = await check_all_fsubs(
            client,
            user_id,
        )

        if not joined:

            await send_fsub_message(
                client,
                message,
                deep_link=(
                    f"sendall_{session_id}_{page}"
                ),
            )

            return

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

        # ----------------------------------------------------
        # LIMIT
        # ----------------------------------------------------

        allowed = await can_make_request(
            user_id,
            FREE_REQUESTS,
        )

        if not allowed:

            await message.reply_text(
                "⚠️ You have reached your request limit."
            )

            return

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

        # ----------------------------------------------------
        # SEND FILES
        # ----------------------------------------------------

        sent_count = 0

        for result in results:

            message_id = get_result_message_id(
                result
            )

            if not message_id:
                continue

            # Check limit before every file.
            allowed = await can_make_request(
                user_id,
                FREE_REQUESTS,
            )

            if not allowed:
                break

            consumed = await consume_request(
                user_id
            )

            if not consumed:
                break

            try:

                await send_database_file(
                    client,
                    user_id,
                    message_id,
                )

                sent_count += 1

            except Exception:

                try:

                    await restore_request(
                        user_id
                    )

                except Exception:
                    pass

        if sent_count == 0:

            await message.reply_text(
                "❌ No files could be sent."
            )

            return

        await message.reply_text(
            f"✅ Sent {sent_count} file(s).",
            reply_markup=file_sent_buttons(),
        )

    except Exception:

        logger.exception(
            "handle_sendall_deep_link failed"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# PAGINATION
# ============================================================

async def get_search_page(
    query: str,
    page: int = 0,
    filters: Optional[dict] = None,
):
    return await search_movies(
        query=query,
        page=page,
        filters=filters,
    )


# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH WITH FILTERS
# ============================================================

async def filtered_search(
    query: str,
    language: Optional[str] = None,
    year: Optional[int] = None,
    season: Optional[int] = None,
    episode: Optional[int] = None,
    quality: Optional[str] = None,
    page: int = 0,
):
    """
    Search using all supported filters.
    """

    filters = normalize_filters(
        {
            "language": language,
            "year": year,
            "season": season,
            "episode": episode,
            "quality": quality,
        }
    )

    return await search_movies(
        query=query,
        page=page,
        filters=filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILTERED RESULT COUNT
# ============================================================

async def has_filtered_results(
    query: str,
    filters: Optional[dict] = None,
):
    results, _ = await search_movies(
        query=query,
        page=0,
        filters=filters,
    )

    return bool(results)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def search(
    query: str,
    page: int = 0,
    filters: Optional[dict] = None,
):
    """
    Compatibility wrapper.
    """

    return await search_movies(
        query=query,
        page=page,
        filters=filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def find_movies(
    query: str,
    page: int = 0,
    filters: Optional[dict] = None,
):
    return await search_movies(
        query=query,
        page=page,
        filters=filters,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

__all__ = [
    "clean_query",
    "normalize_query",
    "escape_regex",
    "create_search_patterns",

    "get_result_title",
    "get_result_message_id",

    "normalize_filters",
    "filter_label",

    "search_movies",
    "advanced_search",
    "search_exact_title",

    "get_available_filters",
    "get_available_languages",
    "get_available_years",
    "get_available_qualities",
    "get_available_seasons",
    "get_available_episodes",

    "create_filtered_search_session",
    "set_search_filters",
    "get_saved_search",
    "search_session",

    "apply_language_filter",
    "apply_year_filter",
    "apply_quality_filter",
    "apply_season_filter",
    "apply_episode_filter",
    "clear_all_filters",

    "send_database_file",

    "handle_file_deep_link",
    "handle_sendall_deep_link",

    "get_search_page",
    "filtered_search",
    "has_filtered_results",

    "search",
    "find_movies",
]

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
