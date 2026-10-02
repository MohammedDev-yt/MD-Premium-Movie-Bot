# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import asyncio
import logging
import re
import time

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from urllib.parse import quote_plus
from html import escape as html_escape
from pyrogram import filters, enums
from pyrogram.errors import MessageNotModified
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

from config import (
    RESULTS_PER_PAGE,
    MAX_RESULTS,
    UPDATES_CHANNEL, 
    DATABASE_CHANNEL_ID
)

UPDATES_URL = "https://t.me/Aero_Unity"

from database import (
    get_user,
    create_user,
    search_media,
    create_search_session,
    get_search_session,
    update_search_session_filters,
    get_search_session_filters,
    delete_search_session,
    get_filter_options,
    get_media_by_message,
    consume_request,
    restore_request,
    can_make_request,
    record_search
)

from handlers.fsub import (
    check_all_fsubs,
    send_fsub_message
)

logger = logging.getLogger(__name__)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

SEARCH_PAGE_SIZE = int(
    RESULTS_PER_PAGE or 10
)

MAX_SEARCH_RESULTS = int(
    MAX_RESULTS or 50
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# QUERY HELPERS
# ============================================================

def clean_query(query):

    if query is None:
        return ""

    query = str(query).strip()

    query = re.sub(
        r"\s+",
        " ",
        query
    )

    return query
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def normalize_query(query):

    query = clean_query(query)

    return query.lower()
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def escape_regex(text):

    return re.escape(
        str(text)
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def create_search_patterns(query):

    query = clean_query(query)

    if not query:
        return []

    words = query.split()

    patterns = []

    for word in words:

        if len(word) >= 2:

            patterns.append(
                re.escape(word)
            )

    if not patterns:
        patterns.append(
            re.escape(query)
        )

    return patterns
    
def get_result_title(result):
    
    if not result:
        return "Unknown File"
        
    file_size = (
        result.get("file_size")
        or result.get("filesize")
        or result.get("size")
        or 0
    )
    
    size_text = ""

    try:
        size_bytes = int(file_size)

        if size_bytes >= 1024 * 1024 * 1024:
            size_text = (
                f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            )

        elif size_bytes >= 1024 * 1024:
            size_text = (
                f"{size_bytes / (1024 * 1024):.2f} MB"
            )

        elif size_bytes >= 1024:
            size_text = (
                f"{size_bytes / 1024:.2f} KB"
            )

    except (TypeError, ValueError):
        pass

    # ========================================================
    # TITLE
    # ========================================================

    title = (
        result.get("title")
        or result.get("file_name")
        or result.get("filename")
        or result.get("name")
        or result.get("caption")
        or "Unknown File"
    )

    title = str(title).strip()

    # ========================================================
    # SEASON
    # ========================================================

    season = (
        result.get("season")
        or result.get("Season")
        or result.get("season_number")
    )

    episode = (
        result.get("episode")
        or result.get("Episode")
        or result.get("episode_number")
    )
    
    data = result.get("data")

    if isinstance(data, dict):

        if not season:
            season = (
                data.get("season")
                or data.get("Season")
                or data.get("season_number")
            )

        if not episode:
            episode = (
                data.get("episode")
                or data.get("Episode")
                or data.get("episode_number")
            )

    season_episode = ""

    if season is not None and episode is not None:

        try:
            season_number = int(
                re.sub(
                    r"[^0-9]",
                    "",
                    str(season)
                )
            )

            episode_number = int(
                re.sub(
                    r"[^0-9]",
                    "",
                    str(episode)
                )
            )

            season_episode = (
                f"S{season_number:02d}"
                f"E{episode_number:02d}"
            )

        except (TypeError, ValueError):
            season_episode = ""

    if not season_episode:

        match = re.search(
            r"\bS(\d{1,2})[\s._-]*E(\d{1,3})\b",
            title,
            re.IGNORECASE
        )

        if match:

            season_episode = (
                f"S{int(match.group(1)):02d}"
                f"E{int(match.group(2)):02d}"
            )

    # ========================================================
    # CLEAN TITLE
    # ========================================================

    title = re.sub(
        r"\s*\|\s*\d+(?:\.\d+)?\s*(?:MB|GB|KB)\s*",
        " ",
        title,
        flags=re.IGNORECASE
    )
    
    title = re.sub(
        r"\s*\|\s*\d{3,4}p\s*",
        " ",
        title,
        flags=re.IGNORECASE
    )

    if season_episode:

        title = re.sub(
            r"\bS\d{1,2}[\s._-]*E\d{1,3}\b",
            " ",
            title,
            flags=re.IGNORECASE
        )
        
    title = re.sub(
        r"\s+",
        " ",
        title
    ).strip()

    title = re.sub(
        r"^[\s|._-]+|[\s|._-]+$",
        "",
        title
    ).strip()

    # ========================================================
    # BUILD BUTTON TEXT
    # ========================================================

    parts = []

    if size_text:
        parts.append(
            f"[{size_text}]"
        )

    if season_episode:
        parts.append(
            f"[{season_episode}]"
        )

    parts.append(
        title
    )

    return " | ".join(parts)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_year_from_result(result):
    title = get_result_title(result)

    match = re.search(
        r"\b(19\d{2}|20\d{2})\b",
        title
    )

    if match:
        return match.group(1)

    return "—"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_message_id(result):

    value = result.get(
        "message_id"
    )

    try:
        return int(value)
    except Exception:
        return None
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_language(result):

    value = result.get(
        "language"
    )

    if value is None:
        return ""

    return str(value).strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_year(result):

    if not result:
        return ""

    # Check database fields
    value = (
        result.get("year")
        or result.get("release_year")
        or result.get("releaseYear")
    )

    if value:
        return str(value).strip()

    # Check nested data
    data = result.get("data")

    if isinstance(data, dict):

        value = (
            data.get("year")
            or data.get("release_year")
            or data.get("releaseYear")
        )

        if value:
            return str(value).strip()

    # Extract year from title / filename / caption
    text = " ".join(
        str(result.get(key, "") or "")
        for key in [
            "title",
            "file_name",
            "filename",
            "name",
            "caption"
        ]
    )

    match = re.search(
        r"\b(19\d{2}|20\d{2})\b",
        text
    )

    if match:
        return match.group(1)

    return ""

    # Try to detect rating from title/caption
    text = " ".join(
        str(result.get(key, "") or "")
        for key in [
            "title",
            "file_name",
            "filename",
            "name",
            "caption"
        ]
    )

    match = re.search(
        r"\b(?:IMDb?\s*)?([0-9](?:\.[0-9])?)\s*(?:/10)?\b",
        text,
        re.IGNORECASE
    )

    if match:
        return match.group(1)

    return ""
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_quality(result):

    # Check database fields first
    quality = (
        result.get("quality")
        or result.get("video_quality")
        or result.get("resolution")
        or result.get("video_resolution")
    )

    if quality:
        return str(quality).strip()

    # If quality is not stored separately,
    # detect it from the file title/name/caption
    text = " ".join(
        str(result.get(key, "") or "")
        for key in [
            "title",
            "file_name",
            "filename",
            "name",
            "caption",
        ]
    )

    patterns = [
        r"\b(HDRip)\b",
        r"\b(4k)\b",
        r"\b(2160p)\b",
        r"\b(1440p)\b",
        r"\b(1080p)\b",
        r"\b(720p)\b",
        r"\b(576p)\b",
        r"\b(480p)\b",
        r"\b(360p)\b",
        r"\b(240p)\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return match.group(1)

    return ""
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def format_file_size(size):

    try:
        size = int(size)
    except Exception:
        return ""

    if size <= 0:
        return ""

    if size >= 1024 * 1024 * 1024:
        return f"{size / (1024 * 1024 * 1024):.2f} GB"

    return f"{size / (1024 * 1024):.0f} MB"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_result_file_size(result):

    value = (
        result.get("file_size")
        or result.get("filesize")
        or result.get("size")
        or 0
    )

    return format_file_size(value)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH RESULT BUTTONS
# ============================================================

def search_result_buttons(
    results,
    session_id,
    page=0,
    has_next=False
):

    buttons = []

    for index, result in enumerate(
        results,
        start=1
    ):

        message_id = get_result_message_id(
            result
        )

        if message_id is None:
            continue

        title = get_result_title(
            result
        )
        
        title = title[:55]

        button_text = f"›› {title}"
        
        buttons.append(
            [
                InlineKeyboardButton(
                    button_text,
                    callback_data=(
                        f"file_{session_id}_"
                        f"{message_id}"
                    )
                )
            ]
        )

    # --------------------------------------------------------
    # SEND ALL + NEXT
    # --------------------------------------------------------

    if results:

        send_all_button = InlineKeyboardButton(
            "• Sᴇɴᴅ Aʟʟ •",
            callback_data=(
                f"sendall_{session_id}_"
                f"{page}"
            )
        )

        next_button = InlineKeyboardButton(
            "• Nᴇxᴛ •",
            callback_data=(
                f"search_page_"
                f"{session_id}_"
                f"{page + 1}"
            )
        )

        if has_next:

            buttons.append(
                [
                    send_all_button,
                    next_button
                ]
            )

        else:

            buttons.append(
                [
                    send_all_button
                ]
            )

    # --------------------------------------------------------
    # FILTER BUTTON
    # --------------------------------------------------------

    buttons.append(
        [
            InlineKeyboardButton(
                "• ғɪʟᴛᴇʀs •",
                callback_data=(
                    f"filters_{session_id}_"
                    f"{page}"
                )
            )
        ]
    )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "• ʙᴀᴄᴋ •",
                callback_data=(
                    f"search_page_"
                    f"{session_id}_"
                    f"{page - 1}"
                )
            )
        )

    if navigation:

        buttons.append(
            navigation
        )

    return InlineKeyboardMarkup(
        buttons
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH TEXT
# ============================================================

def build_search_text(
    query,
    results,
    page=0,
    has_next=False,
    filters_data=None,
    search_time=0,
    requested_by_id=None,
    requested_by_name="User"
):
    start = page * SEARCH_PAGE_SIZE + 1
    end = start + len(results) - 1

    # Get metadata from first result
    first_result = results[0] if results else {}

    title = query.strip()

    year = get_result_year(first_result) or "—"

    language = get_result_language(first_result) or "—"

    # Clickable Telegram user name
    if requested_by_id:
        requested_by = (
            f'<a href="tg://user?id={requested_by_id}">'
            f'{html_escape(requested_by_name or "User")}'
            f'</a>'
        )
    else:
        requested_by = html_escape(
            requested_by_name or "User"
        )

    text = (
        f"<b>›› Tɪᴛʟᴇ:</b> "
        f"{html_escape(str(title))}\n"

        f"<b>›› Lᴀɴɢᴜᴀɢᴇ:</b> "
        f"{html_escape(str(language))}\n"

        f"<b>›› ʀᴇsᴜʟᴛ ɪɴ :</b> "
        f"{search_time:.2f} Sᴇᴄᴏɴᴅs\n"

        f"<b>›› Rᴇǫᴜᴇsᴛᴇᴅ Bʏ : {requested_by}</b>\n"
        
        f"<b>›› Pᴏᴡᴇʀᴇᴅ Bʏ:</b> "
        f"<b>@Aero_Unity</b>\n\n"

        f"<b>Hᴇʀᴇ Aʀᴇ Yᴏᴜʀ Rᴇsᴜʟᴛs</b> 👇"
    )

    return text

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILTER TEXT
# ============================================================

def build_filter_text(
    options,
    current_filters=None
):

    current_filters = (
        current_filters or {}
    )

    text = (
        "⚙️ <b>Sᴇᴀʀᴄh Fɪʟᴛᴇʀs</b>\n\n"
    )

    if current_filters:

        text += "<b>Current:</b>\n"

        for key, value in current_filters.items():

            text += (
                f"• {html_escape(str(key))}: "
                f"{html_escape(str(value))}\n"
            )

        text += "\n"

    languages = options.get(
        "languages",
        []
    )

    seasons = options.get(
        "seasons",
        []
    )

    episodes = options.get(
        "episodes",
        []
    )

    if languages:

        text += (
            "›› <b>Lᴀɴɢᴜᴀɢᴇ</b>\n"
        )

        text += ", ".join(
            str(x)
            for x in languages[:20]
        )

        text += "\n\n"

    if seasons:

        text += (
            "›› <b>Sᴇᴀsᴏɴ</b>\n"
        )

        text += ", ".join(
            str(x)
            for x in seasons[:20]
        )

        text += "\n\n"

    if episodes:

        text += (
            "›› <b>Eᴘɪsᴏᴅᴇ</b>\n"
        )

        text += ", ".join(
            str(x)
            for x in episodes[:20]
        )

        text += "\n\n"

    if not any(
        [
            languages,
            seasons,
            episodes
        ]
    ):

        text += (
            "❌ <b>Nᴏ Fɪʟᴛᴇʀ Oᴘᴛɪᴏɴs Aᴠᴀɪʟᴀʙʟᴇ.</b>"
        )

    return text

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def build_filter_buttons(
    session_id,
    options,
    current_filters=None
):

    current_filters = (
        current_filters or {}
    )

    buttons = []

    languages = options.get(
        "languages",
        []
    )

    seasons = options.get(
        "seasons",
        []
    )

    episodes = options.get(
        "episodes",
        []
    )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILTER TEXT
# ============================================================

def build_filter_text(
    options,
    current_filters=None,
    filter_type=None
):

    current_filters = (
        current_filters or {}
    )

    # --------------------------------------------------------
    # LANGUAGE PAGE
    # --------------------------------------------------------

    if filter_type == "language":

        return (
            "›› <b>Lᴀɴɢᴜᴀɢᴇ Fɪʟᴛᴇʀ</b>\n\n"
            "›› Sᴇʟᴇᴄᴛ ᴀ Lᴀɴɢᴜᴀɢᴇ:"
        )

    # --------------------------------------------------------
    # SEASON PAGE
    # --------------------------------------------------------

    if filter_type == "season":

        return (
            " <b>Sᴇᴀsᴏɴ Fɪʟᴛᴇʀ</b>\n\n"
            "›› Sᴇʟᴇᴄᴛ ᴀ Sᴇᴀsᴏɴ:"
        )

    # --------------------------------------------------------
    # EPISODE PAGE
    # --------------------------------------------------------

    if filter_type == "episode":

        return (
            " <b>Eᴘɪsᴏᴅᴇ Fɪʟᴛᴇʀ</b>\n\n"
            "›› Sᴇʟᴇᴄᴛ ᴀɴ Eᴘɪsᴏᴅᴇ:"
        )

    # --------------------------------------------------------
    # MAIN FILTER PAGE
    # --------------------------------------------------------

    text = (
        "⚙️ <b>Sᴇᴀʀᴄh Fɪʟᴛᴇʀs</b>\n\n"
    )

    if current_filters:

        text += "<b>Cᴜʀʀᴇɴᴛ Fɪʟᴛᴇʀs:</b>\n"

        for key, value in current_filters.items():

            text += (
                f"• {html_escape(str(key))}: "
                f"{html_escape(str(value))}\n"
            )

        text += "\n"

    text += (
        "›› Sᴇʟᴇᴄᴛ ᴡʜᴀᴛ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ғɪʟᴛᴇʀ:"
    )

    return text
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def build_filter_buttons(
    session_id,
    options,
    current_filters=None,
    filter_type=None
):

    current_filters = (
        current_filters or {}
    )

    buttons = []

    # ========================================================
    # LANGUAGE OPTIONS
    # ========================================================

    if filter_type == "language":

        languages = options.get(
            "languages",
            []
        )

        language_row = []

        for language in languages[:30]:

            language_row.append(
                InlineKeyboardButton(
                    f"{language}",
                    callback_data=(
                        f"setfilter_{session_id}_"
                        f"language_{language}"
                    )
                )
            )

            # 3 BUTTONS PER ROW
            if len(language_row) == 3:

                buttons.append(
                    language_row
                )

                language_row = []

        # Remaining buttons
        if language_row:
            buttons.append(
                language_row
            )

        # BACK
        buttons.append(
            [
                InlineKeyboardButton(
                    "• ʙᴀᴄᴋ •",
                    callback_data=(
                        f"filtermenu_{session_id}"
                    )
                )
            ]
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ========================================================
    # SEASON OPTIONS
    # ========================================================

    if filter_type == "season":

        seasons = options.get(
            "seasons",
            []
        )

        season_row = []

        for season in seasons[:30]:

            try:
                season_number = int(season)
            except Exception:
                continue

            season_row.append(
                InlineKeyboardButton(
                    f"S{season_number:02d}",
                    callback_data=(
                        f"setfilter_{session_id}_"
                        f"season_{season_number}"
                    )
                )
            )

            # 3 BUTTONS PER ROW
            if len(season_row) == 3:

                buttons.append(
                    season_row
                )

                season_row = []

        # Remaining buttons
        if season_row:
            buttons.append(
                season_row
            )

        # BACK
        buttons.append(
            [
                InlineKeyboardButton(
                    "• ʙᴀᴄᴋ •",
                    callback_data=(
                        f"filtermenu_{session_id}"
                    )
                )
            ]
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ========================================================
    # EPISODE OPTIONS
    # ========================================================

    if filter_type == "episode":

        episodes = options.get(
            "episodes",
            []
        )

        episode_row = []

        for episode in episodes[:50]:

            try:
                episode_number = int(episode)
            except Exception:
                continue

            episode_row.append(
                InlineKeyboardButton(
                    f"E{episode_number:02d}",
                    callback_data=(
                        f"setfilter_{session_id}_"
                        f"episode_{episode_number}"
                    )
                )
            )

            # 3 BUTTONS PER ROW
            if len(episode_row) == 3:

                buttons.append(
                    episode_row
                )

                episode_row = []

        # Remaining buttons
        if episode_row:
            buttons.append(
                episode_row
            )

        # BACK
        buttons.append(
            [
                InlineKeyboardButton(
                    "• ʙᴀᴄᴋ •",
                    callback_data=(
                        f"filtermenu_{session_id}"
                    )
                )
            ]
        )

        return InlineKeyboardMarkup(
            buttons
        )

    # ========================================================
    # MAIN FILTER MENU
    # ========================================================

    buttons.append(
        [
            InlineKeyboardButton(
                "• Lᴀɴɢᴜᴀɢᴇ •",
                callback_data=(
                    f"filtertype_{session_id}_language"
                )
            ),
            InlineKeyboardButton(
                "• Sᴇᴀsᴏɴ •",
                callback_data=(
                    f"filtertype_{session_id}_season"
                )
            )
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                "• Eᴘɪsᴏᴅᴇ •",
                callback_data=(
                    f"filtertype_{session_id}_episode"
                )
            )
        ]
    )

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    if current_filters:

        buttons.append(
            [
                InlineKeyboardButton(
                    "• Cʟᴇᴀʀ Fɪʟᴛᴇʀs •",
                    callback_data=(
                        f"clearfilters_{session_id}"
                    )
                )
            ]
        )

    # --------------------------------------------------------
    # BACK TO RESULTS
    # --------------------------------------------------------

    buttons.append(
        [
            InlineKeyboardButton(
                "• ʙᴀᴄᴋ •",
                callback_data=(
                    f"filterback_{session_id}"
                )
            )
        ]
    )

    return InlineKeyboardMarkup(
        buttons
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH
# ============================================================

async def search_movies(
    query,
    page=0,
    filters_data=None
):

    query = clean_query(
        query
    )

    if not query:
        return [], False

    try:
        page = max(
            0,
            int(page)
        )
    except Exception:
        page = 0

    skip = (
        page * SEARCH_PAGE_SIZE
    )

    # One extra result determines next page.
    limit = SEARCH_PAGE_SIZE + 1

    results = await search_media(
        query=query,
        skip=skip,
        limit=limit,
        filters=filters_data or {}
    )

    has_next = (
        len(results) > SEARCH_PAGE_SIZE
    )

    results = results[
        :SEARCH_PAGE_SIZE
    ]

    return results, has_next

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def advanced_search(
    query,
    page=0,
    filters_data=None
):

    query = clean_query(
        query
    )

    if not query:
        return [], False

    results, has_next = await search_movies(
        query,
        page,
        filters_data
    )

    return results, has_next

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def search_exact_title(
    query,
    limit=10
):

    results = await search_media(
        query=query,
        skip=0,
        limit=limit,
        filters={}
    )

    return results

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILTER OPTIONS
# ============================================================

async def get_available_filter_options(
    query,
    filters_data=None
):

    return await get_filter_options(
        query=query,
        filters=filters_data or {}
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_years(
    query,
    filters_data=None
):

    options = await get_filter_options(
        query,
        filters_data
    )

    return options.get(
        "years",
        []
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_languages(
    query,
    filters_data=None
):

    options = await get_filter_options(
        query,
        filters_data
    )

    return options.get(
        "languages",
        []
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_qualities(
    query,
    filters_data=None
):

    options = await get_filter_options(
        query,
        filters_data
    )

    return options.get(
        "qualities",
        []
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_seasons(
    query,
    filters_data=None
):

    options = await get_filter_options(
        query,
        filters_data
    )

    return options.get(
        "seasons",
        []
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_available_episodes(
    query,
    filters_data=None
):

    options = await get_filter_options(
        query,
        filters_data
    )

    return options.get(
        "episodes",
        []
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH SESSION HELPERS
# ============================================================

async def create_session(
    user_id,
    query,
    filters_data=None
):

    return await create_search_session(
        user_id=user_id,
        query=query,
        filters=filters_data or {}
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_session(
    session_id,
    user_id
):

    return await get_search_session(
        session_id=session_id,
        user_id=user_id
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def update_filters(
    session_id,
    user_id,
    filters_data
):

    return await update_search_session_filters(
        session_id=session_id,
        user_id=user_id,
        filters=filters_data or {}
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def get_filters(
    session_id,
    user_id
):

    return await get_search_session_filters(
        session_id=session_id,
        user_id=user_id
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# USER HELPER
# ============================================================

async def ensure_user(
    client,
    user_id
):

    user = await get_user(
        user_id
    )

    if user:
        return user

    try:

        chat = await client.get_users(
            user_id
        )

        first_name = (
            chat.first_name
            or "User"
        )

        username = (
            chat.username
            or ""
        )

    except Exception:

        first_name = "User"
        username = ""

    return await create_user(
        user_id=user_id,
        first_name=first_name,
        username=username
    )
    
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# AUTO DELETE FILE AFTER 5 MINUTES
# ============================================================

async def delete_file_after_5_minutes(message):

    await asyncio.sleep(300)

    try:

        await message.delete()

        logger.info(
            "FILE AUTO-DELETED AFTER 5 MINUTES | message_id=%s",
            message.id
        )

    except Exception as e:

        logger.warning(
            "FILE AUTO-DELETE FAILED | message_id=%s | %s",
            getattr(message, "id", "unknown"),
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

async def delete_search_results_after_5_minutes(client, chat_id, message_id):
    try:
        await asyncio.sleep(300)  # 5 minutes

        try:
            await client.delete_messages(
                chat_id,
                message_id
            )
        except Exception:
            pass

    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.warning(
            f"Failed to delete search results "
            f"{chat_id}:{message_id}: {e}"
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# DATABASE FILE DELIVERY
# ============================================================

async def send_database_file(
    client,
    chat_id,
    message_id
):

    try:

        message_id = int(
            message_id
        )

    except Exception:

        return None

    try:

        copied = await client.copy_message(
            chat_id=chat_id,
            from_chat_id=DATABASE_CHANNEL_ID,
            message_id=message_id
        )

        if copied.caption:

            clickable_caption = (
                f'<a href="{UPDATES_URL}">'
                f'<b>{html_escape(copied.caption)}</b>'
                f'</a>'
            )

            await client.edit_message_caption(
                chat_id=chat_id,
                message_id=copied.id,
                caption=clickable_caption,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "• Uᴘᴅᴀᴛᴇs •",
                            url=UPDATES_URL
                        )
                    ]
                ])
            )

        else:

            await client.edit_message_reply_markup(
                chat_id=chat_id,
                message_id=copied.id,
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "• Uᴘᴅᴀᴛᴇs •",
                            url=UPDATES_URL
                        )
                    ]
                ])
            )

        asyncio.create_task(
            delete_file_after_5_minutes(copied)
        )

        return copied

    except Exception as e:

        logger.error(
            "DATABASE FILE SEND ERROR: %s",
            e,
            exc_info=True
        )

        return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# FILE DEEP LINK
# ============================================================

async def handle_file_deep_link(
    client,
    message,
    message_id,
    user_id=None
):

    if user_id is None:

        if not message.from_user:
            return

        user_id = message.from_user.id

    # --------------------------------------------------------
    # VALIDATE MESSAGE ID
    # --------------------------------------------------------

    try:

        message_id = int(message_id)

    except (TypeError, ValueError):

        await client.send_message(
            user_id,
            "❌ <b>Invalid file ID.</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # --------------------------------------------------------
    # PRIVATE ONLY
    # --------------------------------------------------------

    if message.chat.type != enums.ChatType.PRIVATE:

        return

    # --------------------------------------------------------
    # MAKE SURE USER EXISTS
    # --------------------------------------------------------

    await ensure_user(
        client,
        user_id
    )

    not_joined = await check_all_fsubs(
        client,
        user_id
    )

    if not_joined:

        await send_fsub_message(
            client,
            message,
            not_joined,
            deep_link=f"file_{message_id}"
        )

        return

    # --------------------------------------------------------
    # GET MEDIA FROM DATABASE
    # --------------------------------------------------------

    try:

        media = await get_media_by_message(
            DATABASE_CHANNEL_ID,
            message_id
        )

    except Exception as e:

        logger.exception(
            "MEDIA LOOKUP ERROR | user=%s | message_id=%s | error=%s",
            user_id,
            message_id,
            e
        )

        await client.send_message(
            user_id,
            "‼️ <b>Database error while finding this file.</b>\n\n"
            "Please contact the owner.",
            parse_mode=enums.ParseMode.HTML
        )

        return

    if not media:

        await client.send_message(
            user_id,
            "<b>This Movie Not Found in Database</b>\n\n"
            "<b>Request To Owner "
            "[@Mr_Mohammed_29] To add movie</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # --------------------------------------------------------
    # REQUEST LIMIT CHECK
    # --------------------------------------------------------

    try:

        allowed = await can_make_request(
            user_id
        )

    except Exception as e:

        logger.exception(
            "REQUEST CHECK ERROR | user=%s | error=%s",
            user_id,
            e
        )

        await client.send_message(
            user_id,
            "‼️ <b>Unable to check your request balance.</b>\n\n"
            "Please try again.",
            parse_mode=enums.ParseMode.HTML
        )

        return

    if not allowed:

        await client.send_message(
            user_id,
            "‼️ <b><i>Your Free Requests Completed.</i></b>\n\n"
            "<b>Please activate Premium to continue.</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # --------------------------------------------------------
    # CONSUME REQUEST
    # --------------------------------------------------------

    try:

        consumed = await consume_request(
            user_id
        )

    except Exception as e:

        logger.exception(
            "CONSUME REQUEST ERROR | user=%s | error=%s",
            user_id,
            e
        )

        await client.send_message(
            user_id,
            "‼️ <b>Unable to process your request.</b>\n\n"
            "Please try again.",
            parse_mode=enums.ParseMode.HTML
        )

        return

    if not consumed:

        await client.send_message(
            user_id,
            "❌ <b>No requests remaining.</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # --------------------------------------------------------
    # SEND EXACT DATABASE FILE
    # --------------------------------------------------------

    sent = await send_database_file(
        client=client,
        chat_id=user_id,
        message_id=message_id
    )

    # --------------------------------------------------------
    # DELIVERY FAILED
    # --------------------------------------------------------

    if not sent:

        try:

            await restore_request(
                user_id
            )

        except Exception as e:

            logger.warning(
                "FAILED TO RESTORE REQUEST | "
                "user=%s | error=%s",
                user_id,
                e
            )

        await client.send_message(
            user_id,
            "‼️ <b>System Crashing ...</b>\n\n"
            "<b>Ask The Owner "
            "[@Mr_Mohammed_29] To Solve The Issue</b>",
            parse_mode=enums.ParseMode.HTML
        )

        return

    # --------------------------------------------------------
    # WARNING MESSAGE
    # --------------------------------------------------------

    try:

        warning_message = await client.send_message(
            user_id,
            "<b>⏳️ ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs...</b>\n\n"
            "<b>›› ʏᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 min</b>\n"
            "<b>›› sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ᴏʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ</b>\n\n"
            "<b>ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴘʟᴀʏᴇʀ ᴏʀ ᴍx ᴘʟᴀʏᴇʀ ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=sent.id
        )

        asyncio.create_task(
            delete_file_after_5_minutes(
                warning_message
            )
        )

    except Exception as e:

        logger.warning(
            "WARNING MESSAGE ERROR | user=%s | error=%s",
            user_id,
            e
        )

    # --------------------------------------------------------
    # RECORD SEARCH
    # --------------------------------------------------------

    try:

        await record_search(
            str(
                media.get(
                    "title",
                    media.get(
                        "file_name",
                        ""
                    )
                )
            )
        )

    except Exception:

        pass

    logger.info(
        "FILE SENT SUCCESSFULLY | user=%s | message_id=%s",
        user_id,
        message_id
    )

    return sent

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# GET ALL RESULTS FOR SEND ALL
# ============================================================

async def get_all_sendall_results(
    query,
    filters_data=None
):
    """
    Fetch ALL matching files from MongoDB.

    Normal search is paginated.
    Send All must continue through every database page.
    """

    filters_data = filters_data or {}

    all_results = []
    skip = 0
    batch_size = 100

    while True:
        try:
            batch = await search_media(
                query=query,
                skip=skip,
                limit=batch_size,
                filters=filters_data
            )

        except Exception as e:
            logger.error(
                "SEND ALL DATABASE SEARCH ERROR: %s",
                e,
                exc_info=True
            )
            break

        if not batch:
            break

        all_results.extend(batch)

        # Last batch reached
        if len(batch) < batch_size:
            break

        skip += batch_size

    logger.info(
        "SEND ALL: %s files found for query=%s filters=%s",
        len(all_results),
        query,
        filters_data
    )

    return all_results

# ============================================================
# SEND ALL DEEP LINK
# ============================================================

async def handle_sendall_deep_link(
    client,
    message,
    session_id,
    page,
    user_id=None
):

    if user_id is None:

        if not message.from_user:
            return

        user_id = message.from_user.id

    # --------------------------------------------------------
    # PRIVATE ONLY
    # --------------------------------------------------------

    if message.chat.type != enums.ChatType.PRIVATE:

        return

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    await ensure_user(
        client,
        user_id
    )

    # --------------------------------------------------------
    # FORCE SUB
    # --------------------------------------------------------

    not_joined = await check_all_fsubs(
        client,
        user_id
    )

    if not_joined:

        await send_fsub_message(
            client,
            message,
            not_joined,
            deep_link=(
                f"sendall_{session_id}_{page}"
            )
        )

        return

    # --------------------------------------------------------
    # SESSION
    # --------------------------------------------------------

    session = await get_search_session(
        session_id=session_id,
        user_id=user_id
    )

    if not session:

        await message.reply_text(
            "<b>Sᴇssɪᴏɴ E xᴘɪʀᴇᴅ, Sᴇᴀʀᴄ Aɢᴀɪɴ.</b>"
        )

        return

    # --------------------------------------------------------
    # GET ORIGINAL SEARCH QUERY
    # --------------------------------------------------------

    query = session.get(
        "query",
        ""
    )

    # --------------------------------------------------------
    # GET SELECTED FILTERS
    # --------------------------------------------------------

    filters_data = session.get(
        "filters",
        {}
    ) or {}

    results = await get_all_sendall_results(
        query=query,
        filters_data=filters_data
    )

    if not results:

        await message.reply_text(
            "<b>Nᴏ Fɪʟᴇs Fᴏᴜɴᴅ Fᴏʀ Tʜᴇ Sᴇʟᴇᴄᴛᴇᴅ Fɪʟᴛᴇʀ. 😢</b>"
        )

        return

    # --------------------------------------------------------
    # SEND ALL RESULTS
    # --------------------------------------------------------

    sent_count = 0
    failed_count = 0
    skipped_count = 0

    last_sent = None

    total_results = len(
        results
    )

    # --------------------------------------------------------
    # SEND EVERY MATCHING FILE
    # --------------------------------------------------------

    for result in results:

        media_message_id = get_result_message_id(
            result
        )

        if media_message_id is None:

            skipped_count += 1

            continue

        # ----------------------------------------------------
        # CHECK REQUEST BALANCE
        # ----------------------------------------------------

        try:

            allowed = await can_make_request(
                user_id
            )

        except Exception as e:

            logger.error(
                "SEND ALL REQUEST CHECK ERROR | "
                "user=%s | error=%s",
                user_id,
                e,
                exc_info=True
            )

            break

        if not allowed:

            break

        # ----------------------------------------------------
        # CONSUME REQUEST
        # ----------------------------------------------------

        try:

            consumed = await consume_request(
                user_id
            )

        except Exception as e:

            logger.error(
                "SEND ALL CONSUME ERROR | "
                "user=%s | error=%s",
                user_id,
                e,
                exc_info=True
            )

            break

        if not consumed:

            break

        # ----------------------------------------------------
        # SEND FILE
        # ----------------------------------------------------

        sent = await send_database_file(
            client=client,
            chat_id=user_id,
            message_id=media_message_id
        )

        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        if sent:

            sent_count += 1

            last_sent = sent

        # ----------------------------------------------------
        # FAILED
        # ----------------------------------------------------

        else:

            failed_count += 1

            try:

                await restore_request(
                    user_id
                )

            except Exception as e:

                logger.warning(
                    "FAILED TO RESTORE REQUEST | "
                    "user=%s | error=%s",
                    user_id,
                    e
                )

    # --------------------------------------------------------
    # ONE WARNING AFTER ALL FILES
    # --------------------------------------------------------

    if sent_count > 0:

        try:

            warning_message = await client.send_message(
                user_id,

                "<b>⏳️ ᴅᴜᴇ ᴛᴏ ᴄᴏᴘʏʀɪɢʜᴛ ɪssᴜᴇs...</b>\n\n"

                "<b>›› ʏᴏᴜʀ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 min</b>\n"

                "<b>›› sᴏ ᴘʟᴇᴀsᴇ ғᴏʀᴡᴀʀᴅ ᴛʜᴇᴍ ᴛᴏ ᴀɴʏ ᴏᴛʜᴇʀ ᴘʟᴀᴄᴇ ᴏʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ғᴏʀ ғᴜᴛᴜʀᴇ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ</b>\n\n"

                "<b>ɴᴏᴛᴇ : ᴜsᴇ ᴠʟᴄ ᴘʟᴀʏᴇʀ ᴏʀ mx player ᴛᴏ ᴡᴀᴛᴄʜ ᴛʜᴇ ᴇᴘɪsᴏᴅᴇs ᴡɪᴛʜ ɢᴏᴏᴅ ᴇxᴘᴇʀɪᴇɴᴄᴇ</b>",

                parse_mode=enums.ParseMode.HTML,

                reply_to_message_id=(
                    last_sent.id
                    if last_sent
                    else None
                )
            )

            asyncio.create_task(
                delete_file_after_5_minutes(
                    warning_message
                )
            )

        except Exception as e:

            logger.warning(
                "SEND ALL WARNING MESSAGE ERROR: %s",
                e
            )

    # --------------------------------------------------------
    # LOG
    # --------------------------------------------------------

    logger.info(
        "SEND ALL COMPLETED | "
        "user=%s | total_found=%s | sent=%s | "
        "failed=%s | skipped=%s",
        user_id,
        total_results,
        sent_count,
        failed_count,
        skipped_count
    )
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REFRESH SEARCH RESULTS
# ============================================================

async def refresh_filtered_results(
    client,
    message,
    session_id,
    page=0
):

    user_id = message.from_user.id

    session = await get_search_session(
        session_id,
        user_id
    )

    if not session:
        return

    query = session.get(
        "query",
        ""
    )

    filters_data = session.get(
        "filters",
        {}
    ) or {}

    results, has_next = await search_movies(
        query=query,
        page=page,
        filters_data=filters_data
    )

    text = build_search_text(
        query=query,
        results=results,
        page=page,
        has_next=has_next,
        filters_data=filters_data
    )

    keyboard = search_result_buttons(
        results=results,
        session_id=session_id,
        page=page,
        has_next=has_next
    )

    try:

        await message.edit_text(
            text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:

        logger.error(
            "REFRESH SEARCH ERROR: %s",
            e
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# REGISTER SEARCH HANDLERS
# ============================================================

def register_search_handlers(app):

    # ========================================================
    # NORMAL TEXT SEARCH
    # ========================================================

    @app.on_message(
        filters.text
        & ~filters.command([
            "start",
            "alive",
            "gentoken",
            "token",
            "redeem",
            "plans",
            "myplan",
            "id",
            "info",
            "font",
            "trendlist",
            "generatecode",
            "codes",
            "addfsub",
            "delfsub",
            "fsublist",
            "channel",
            "premiumuser",
            "activate",
            "deactivate",
            "addpremium",
            "removepremium",
            "stats",
            "indexstatus",
            "resetindex",
            "ban",
            "unban",
            "banlist",
            "maintenance",
            "broadcast",
            "clearjunk",
            "clearjunkgroup",
            "plink",
            "pbatch",
            "batch",
            "video",
            "telegraph",
            "share",
            "system",
            "addadmin",
            "removeadmin",
            "adminlist",
            "warn",
            "unwarn",
            "warningslist",
            "reload",
            "optimize"
        ])
    )
    async def movie_search_handler(
        client,
        message
    ):
        # ====================================================
        # CHECK IF USER IS MUTED
        # ====================================================

        if not message.from_user:
            return

        query = clean_query(
            message.text
        )

        if not query:
            return

        if query.startswith("/"):
            return

        user_id = message.from_user.id

        logger.info(
            "Movie search from %s: %s",
            user_id,
            query
        )

        await ensure_user(
            client,
            user_id
        )

        # ----------------------------------------------------
        # FORCE SUB
        # ----------------------------------------------------

        if message.chat.type == enums.ChatType.PRIVATE:

            not_joined = await check_all_fsubs(
                client,
                user_id
            )

            if not_joined:

                await send_fsub_message(
                    client,
                    message,
                    not_joined
                )      

                return

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        try:

            await record_search(
                query
            )

        except Exception:

            pass

        search_start = time.perf_counter()

        results, has_next = await search_movies(
            query=query,
            page=0,
            filters_data={}
        )

        search_time = time.perf_counter() - search_start

        if not results:

            await message.reply_text(
                "<b>😴 ʏᴏᴜʀ ʀᴇǫᴜᴇsᴛ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ.</b>\n\n",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "• Rᴇǫᴜᴇsᴛ Tᴏ Oᴡɴᴇʀ •",
                            url="https://t.me/Mr_Mohammed_29"
                        ),
                        InlineKeyboardButton(
                            "• Cʜᴇᴄᴋ Sᴘᴇʟʟɪɴɢ •",
                            url=("https://www.google.com/search?q="
                                         f"{quote_plus(query)}"
                            )
                        )
                    ]
                ])
            )

            return
  
        # ----------------------------------------------------
        # SESSION
        # ----------------------------------------------------

        session_id = await create_search_session(
            user_id=user_id,
            query=query,
            filters={}
        )

        text = build_search_text(
            query=query,
            results=results,
            page=0,
            has_next=has_next,
            filters_data={},
            search_time=search_time,
            requested_by_id=user_id,
            requested_by_name=(
                message.from_user.first_name
                or "User"
            )
        )

        keyboard = search_result_buttons(
            results=results,
            session_id=session_id,
            page=0,
            has_next=has_next
        )

        sent = await message.reply_text(
            text,
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.HTML
        )

        asyncio.create_task(
            delete_search_results_after_5_minutes(
                client,
                sent.chat.id,
                sent.id
            )
        )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # SEARCH PAGE
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^search_page_[a-fA-F0-9]+_\d+$"
        )
    )
    async def search_page_callback(
        client,
        callback
    ):

        parts = callback.data.split(
            "_"
        )

        if len(parts) != 4:
            await callback.answer(
                "Invalid page.",
                show_alert=True
            )
            return

        session_id = parts[2]

        try:
            page = int(parts[3])
        except Exception:
            page = 0

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired. Search again.",
                show_alert=True
            )

            return

        query = session.get(
            "query",
            ""
        )

        filters_data = session.get(
            "filters",
            {}
        ) or {}

        results, has_next = await search_movies(
            query=query,
            page=page,
            filters_data=filters_data
        )

        if not results:

            await callback.answer(
                "No more results.",
                show_alert=True
            )

            return

        try:
            requester = await client.get_users(
                user_id
            )

            requested_by_name = (
                requester.first_name
                or "User"
            )

        except Exception:
            requested_by_name = "User"

        text = build_search_text(
            query=query,
            results=results,
            page=page,
            has_next=has_next,
            filters_data=filters_data,
            search_time=0,
            requested_by_id=user_id,
        requested_by_name=requested_by_name
        )

        keyboard = search_result_buttons(
            results=results,
            session_id=session_id,
            page=page,
            has_next=has_next
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:

            logger.error(
                "SEARCH PAGE EDIT ERROR: %s",
                e
            )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # FILE BUTTON
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^file_[a-fA-F0-9]+_\d+$"
        )
    )
    async def file_callback(
        client,
        callback
    ):

        parts = callback.data.split(
            "_"
        )

        if len(parts) != 3:

            await callback.answer(
                "Invalid file.",
                show_alert=True
            )

            return

        session_id = parts[1]

        try:

            message_id = int(
                parts[2]
            )

        except Exception:

            await callback.answer(
                "Invalid file ID.",
                show_alert=True
            )

            return

        user_id = callback.from_user.id

        if callback.message.chat.type != enums.ChatType.PRIVATE:

            me = await client.get_me()

            bot_username = (
                me.username
                or ""
            )

            deep_link = (
                f"https://t.me/"
                f"{bot_username}"
                f"?start=file_{message_id}"
            )

            await callback.answer(
                url=deep_link
            )

            return

        # ----------------------------------------------------
        # PRIVATE
        # ----------------------------------------------------

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired. Search again.",
                show_alert=True
            )

            return

        await callback.answer(
            "›› sᴇɴᴅɪɴɢ ꜰɪʟᴇ...."
        )

        await handle_file_deep_link(
            client=client,
            message=callback.message,
            message_id=message_id,
            user_id=user_id
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # SEND ALL
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^sendall_[a-fA-F0-9]+_\d+$"
        )
    )
    async def sendall_callback(
        client,
        callback
    ):

        parts = callback.data.split(
            "_"
        )

        if len(parts) != 3:

            await callback.answer(
                "Invalid request.",
                show_alert=True
            )

            return

        session_id = parts[1]

        try:
            page = int(parts[2])
        except Exception:
            page = 0

        user_id = callback.from_user.id

        # ----------------------------------------------------
        # GROUP
        # ----------------------------------------------------

        if callback.message.chat.type != enums.ChatType.PRIVATE:

            me = await client.get_me()

            bot_username = (
                me.username
                or ""
            )

            deep_link = (
                f"https://t.me/"
                f"{bot_username}"
                f"?start="
                f"sendall_{session_id}_{page}"
            )

            await callback.answer(
                url=deep_link
            )

            return

        # ----------------------------------------------------
        # PRIVATE
        # ----------------------------------------------------

        await callback.answer(
            "›› ᴘʀᴇᴘᴀʀɪɴɢ ꜰɪʟᴇs ᴛᴏ sᴇɴᴅ...."
        )

        await handle_sendall_deep_link(
            client=client,
            message=callback.message,
            session_id=session_id,
            page=page,
            user_id=user_id
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # FILTER PAGE
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^filters_[a-fA-F0-9]+_\d+$"
        )
    )
    async def filters_callback(
        client,
        callback
    ):

        parts = callback.data.split(
            "_"
        )

        if len(parts) != 3:

            await callback.answer(
                "Invalid filter.",
                show_alert=True
            )

            return

        session_id = parts[1]

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        query = session.get(
            "query",
            ""
        )

        current_filters = session.get(
            "filters",
            {}
        ) or {}

        options = await get_filter_options(
            query=query,
            filters=current_filters
        )

        text = build_filter_text(
            options,
            current_filters
        )

        keyboard = build_filter_buttons(
            session_id,
            options,
            current_filters
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except MessageNotModified:
  
            pass

        except Exception as e:

           logger.error(
               "FILTER EDIT ERROR: %s",
               e,
               exc_info=True
           )

        await callback.answer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # FILTER TYPE
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^filtertype_[a-fA-F0-9]+_(language|season|episode)$"
        )
    )
    async def filter_type_callback(
        client,
        callback
    ):

        parts = callback.data.split("_")

        if len(parts) != 3:

            await callback.answer(
                "Invalid filter.",
                show_alert=True
            )

            return

        session_id = parts[1]
        filter_type = parts[2]

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        query = session.get(
            "query",
            ""
        )

        current_filters = session.get(
            "filters",
            {}
        ) or {}

        options = await get_filter_options(
            query=query,
            filters=current_filters
        )

        text = build_filter_text(
            options,
            current_filters,
            filter_type=filter_type
        )

        keyboard = build_filter_buttons(
            session_id,
            options,
            current_filters,
            filter_type=filter_type
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except MessageNotModified:

            pass

        except Exception as e:

            logger.error(
                "FILTER TYPE EDIT ERROR: %s",
                e,
                exc_info=True
            )

        await callback.answer()


    # ========================================================
    # FILTER MENU BACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^filtermenu_[a-fA-F0-9]+$"
        )
    )
    async def filter_menu_callback(
        client,
        callback
    ):

        session_id = callback.data.split(
            "_",
            1
        )[1]

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        query = session.get(
            "query",
            ""
        )

        current_filters = session.get(
            "filters",
            {}
        ) or {}

        options = await get_filter_options(
            query=query,
            filters=current_filters
        )

        text = build_filter_text(
            options,
            current_filters
        )

        keyboard = build_filter_buttons(
            session_id,
            options,
            current_filters
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except MessageNotModified:

            pass

        except Exception as e:

            logger.error(
                "FILTER MENU BACK ERROR: %s",
                e,
                exc_info=True
            )

        await callback.answer()

    # ========================================================
    # SET FILTER
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^setfilter_[a-fA-F0-9]+_(language|season|episode)_.+$"
        )
    )
    async def set_filter_callback(
        client,
        callback
    ):

        parts = callback.data.split(
            "_",
            3
        )

        if len(parts) != 4:

            await callback.answer(
                "Invalid filter.",
                show_alert=True
            )

            return

        session_id = parts[1]
        field = parts[2]
        value = parts[3]

        user_id = callback.from_user.id

        # ----------------------------------------------------
        # GET SESSION
        # ----------------------------------------------------

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        # ----------------------------------------------------
        # CONVERT SEASON / EPISODE TO INTEGER
        # ----------------------------------------------------

        if field in (
            "season",
            "episode"
        ):

            try:
                value = int(value)

            except Exception:

                await callback.answer(
                    "Invalid value.",
                    show_alert=True
                )

                return

        # ----------------------------------------------------
        # CURRENT FILTERS
        # ----------------------------------------------------

        current_filters = session.get(
            "filters",
            {}
        ) or {}

        # ====================================================
        # SEASON SELECTED
        # ====================================================

        if field == "season":

            # Save selected season
            current_filters["season"] = value

            # Remove old episode selection
            current_filters.pop(
                "episode",
                None
            )

            await update_search_session_filters(
                session_id=session_id,
                user_id=user_id,
                filters=current_filters
            )

            query = session.get(
                "query",
                ""
            )

            # ------------------------------------------------
            # GET EPISODES FOR SELECTED SEASON
            # ------------------------------------------------

            episode_filters = dict(
                current_filters
            )

            episode_filters["season"] = value

            episode_filters.pop(
                "episode",
                None
            )

            options = await get_filter_options(
                query=query,
                filters=episode_filters
            )

            episodes = options.get(
                "episodes",
                []
            )

            # ------------------------------------------------
            # EPISODE SCREEN
            # ------------------------------------------------

            text = (
                f"✨ <b>Sᴇᴀsᴏɴ "
                f"{int(value):02d} — Sᴇʟᴇᴄᴛ Eᴘɪsᴏᴅᴇ</b> ✨\n\n"
                f"›› <b>Sᴇʟᴇᴄᴛ Aɴ Eᴘɪsᴏᴅᴇ Tᴏ Cᴏɴᴛɪɴᴜᴇ:</b>"
            )

            buttons = []

            # ------------------------------------------------
            # EPISODE BUTTONS
            # ------------------------------------------------

            episode_row = []

            for episode in episodes[:50]:

                try:
                    episode_number = int(
                        episode
                    )
                except Exception:
                    continue

                episode_row.append(
                    InlineKeyboardButton(
                        f"Eᴘ {episode_number:02d}",
                        callback_data=(
                            f"setfilter_{session_id}_"
                            f"episode_{episode_number}"
                        )
                    )
                )

                # 3 buttons per row
                if len(episode_row) == 3:

                    buttons.append(
                        episode_row
                    )

                    episode_row = []

            if episode_row:

                buttons.append(
                    episode_row
                )

            # ------------------------------------------------
            # SEND ALL SEASON
            # ------------------------------------------------

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"➜ Sᴇɴᴅ Aʟʟ Sᴇᴀsᴏɴ "
                        f"{int(value):02d}",
                        callback_data=(
                            f"sendseason_{session_id}_"
                            f"{int(value)}"
                        )
                    )
                ]
            )

            # ------------------------------------------------
            # BACK TO SEASONS
            # ------------------------------------------------

            buttons.append(
                [
                    InlineKeyboardButton(
                        "• Bᴀᴄᴋ Tᴏ Sᴇᴀsᴏɴs •",
                        callback_data=(
                            f"filtertype_{session_id}_season"
                        )
                    )
                ]
            )

            keyboard = InlineKeyboardMarkup(
                buttons
            )

            try:

                await callback.message.edit_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )

            except MessageNotModified:

                pass

            except Exception as e:

                logger.error(
                    "SEASON EPISODE MENU ERROR: %s",
                    e,
                    exc_info=True
                )

            await callback.answer(
                f"Season {int(value):02d} selected."
            )

            return

        # ====================================================
        # EPISODE SELECTED
        # ====================================================

        if field == "episode":

            # Keep selected season
            season = current_filters.get(
                "season"
            )

            # Save episode
            current_filters["episode"] = value

            await update_search_session_filters(
                session_id=session_id,
                user_id=user_id,
                filters=current_filters
            )

            # ------------------------------------------------
            # SEARCH FILES
            # ------------------------------------------------

            query = session.get(
                "query",
                ""
            )

            results, has_next = await search_movies(
                query=query,
                page=0,
                filters_data=current_filters
            )

            # ------------------------------------------------
            # NO FILES
            # ------------------------------------------------

            if not results:

                await callback.answer(
                    "No files found for this episode.",
                    show_alert=True
                )

                return

            # ------------------------------------------------
            # BUILD RESULT TEXT
            # ------------------------------------------------

            text = build_search_text(
                query=query,
                results=results,
                page=0,
                has_next=has_next,
                filters_data=current_filters
            )

            # ------------------------------------------------
            # RESULT BUTTONS
            # ------------------------------------------------

            keyboard = search_result_buttons(
                results=results,
                session_id=session_id,
                page=0,
                has_next=has_next
            )

            try:

                await callback.message.edit_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )

            except MessageNotModified:

                pass

            except Exception as e:

                logger.error(
                    "EPISODE RESULT ERROR: %s",
                    e,
                    exc_info=True
                )

            await callback.answer(
                f"S{int(season or 0):02d}E{int(value):02d} files loaded."
            )

            return

        # ====================================================
        # LANGUAGE SELECTED
        # ====================================================

        if field == "language":

            current_filters["language"] = value

            await update_search_session_filters(
                session_id=session_id,
                user_id=user_id,
                filters=current_filters
            )

            query = session.get(
                "query",
                ""
            )

            results, has_next = await search_movies(
                query=query,
                page=0,
                filters_data=current_filters
            )

            if not results:

                await callback.answer(
                    "No files found.",
                    show_alert=True
                )

                return

            text = build_search_text(
                query=query,
                results=results,
                page=0,
                has_next=has_next,
                filters_data=current_filters
            )

            keyboard = search_result_buttons(
                results=results,
                session_id=session_id,
                page=0,
                has_next=has_next
            )

            try:

                await callback.message.edit_text(
                    text,
                    reply_markup=keyboard,
                    parse_mode=enums.ParseMode.HTML
                )

            except MessageNotModified:

                pass

            except Exception as e:

                logger.error(
                    "LANGUAGE RESULT ERROR: %s",
                    e,
                    exc_info=True
                )

            await callback.answer(
                "Language filter applied."
            )

    # ============================================================
    # SEND ALL SEASON
    # ============================================================

    @app.on_callback_query(
        filters.regex(
            r"^sendseason_[a-fA-F0-9]+_\d+$"
        )
    )
    async def send_all_season_callback(
        client,
        callback
    ):
        try:
            data = callback.data.split("_")
 
            session_id = data[1]
            season = int(data[2])

        except Exception:
            await callback.answer(
                "❌ Invalid request.",
                show_alert=True
            )
            return

        # --------------------------------------------------------
        # GET SEARCH SESSION
        # --------------------------------------------------------

        session = await get_search_session(
            session_id,
            callback.from_user.id
        )

        if not session:
            await callback.answer(
                "⚠️ Sᴇᴀʀᴄʜ sᴇssɪᴏɴ ᴇxᴘɪʀᴇᴅ.",
                show_alert=True
            )
            return

        query = session.get(
            "query",
            ""
        )

        # --------------------------------------------------------
        # EXISTING FILTERS
        # --------------------------------------------------------

        filters_data = dict(
            session.get(
                "filters",
                {}
            ) or {}
        )

        # Force selected season
        filters_data["season"] = season

        # Season Send All means every episode
        filters_data.pop(
            "episode",
            None
        )

        # --------------------------------------------------------
        # FETCH ALL FILES
        # --------------------------------------------------------

        await callback.answer(
            f"📤 Sᴇɴᴅɪɴɢ Aʟʟ S{season:02d} ғɪʟᴇs..."
        )

        try:
            results = await get_all_sendall_results(
                query=query,
                filters_data=filters_data
            )

        except Exception as e:
            logger.error(
                "SEND ALL SEASON ERROR: %s",
                e,
                exc_info=True
            )

            await callback.message.reply_text(
                "❌ Fᴀɪʟᴇᴅ ᴛᴏ ʟᴏᴀᴅ sᴇᴀsᴏɴ ғɪʟᴇs."
            )
            return

        if not results:
            await callback.message.reply_text(
                f"❌ Nᴏ ғɪʟᴇs ғᴏᴜɴᴅ ғᴏʀ S{season:02d}."
            )
            return

        sent = 0
        failed = 0

        # Store all sent messages so we can delete them later
        sent_messages = []

        for item in results:

            try:
                message_id = item.get(
                    "message_id"
                )   

                if not message_id:
                    failed += 1
                    continue

                sent_message = await send_database_file(
                    client=client,
                    chat_id=callback.from_user.id,
                    message_id=message_id
                )

                if sent_message:
                    sent_messages.append(
                        sent_message
                    )

                sent += 1

            except Exception as e:

                failed += 1

                logger.warning(
                    "Failed to send season file %s: %s",
                    item.get("message_id"),
                    e
                )

        # --------------------------------------------------------
        # DELETE SENDING STATUS
        # --------------------------------------------------------

        try:
            await status_message.delete()
        except Exception:
            pass

        # --------------------------------------------------------
        # WARNING MESSAGE
        # --------------------------------------------------------

        warning_message = await callback.message.reply_text(
            "⚠️ Wᴀʀɴɪɴɢ\n\n"
            "📥 Pʟᴇᴀsᴇ sᴀᴠᴇ ᴛʜᴇ ғɪʟᴇs ᴀʙᴏᴠᴇ ᴛᴏ ʏᴏᴜʀ "
            "Sᴀᴠᴇᴅ Mᴇssᴀɢᴇs ғᴏʀ ʟᴀᴛᴇʀ ᴜsᴇ.\n\n"
            "⚠️ Tʜᴇ ғɪʟᴇs ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ɪɴ 5 ᴍɪɴᴜᴛᴇs.\n\n"
            "💾 Sᴀᴠᴇ ᴛʜᴇᴍ ɴᴏᴡ."
        )

        # --------------------------------------------------------
        # WAIT 5 MINUTES
        # --------------------------------------------------------

        await asyncio.sleep(300)

        # --------------------------------------------------------
        # DELETE ALL SENT FILES
        # --------------------------------------------------------

        for sent_message in sent_messages:
 
            try:
                await sent_message.delete()

            except Exception:
                pass

        # --------------------------------------------------------
        # DELETE WARNING
        # --------------------------------------------------------

        try:
            await warning_message.delete()

        except Exception:
            pass
            
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # CLEAR FILTERS
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^clearfilters_[a-fA-F0-9]+$"
        )
    )
    async def clear_filters_callback(
        client,
        callback
    ):

        session_id = callback.data.split(
            "_",
            1
        )[1]

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        await update_search_session_filters(
            session_id=session_id,
            user_id=user_id,
            filters={}
        )

        query = session.get(
            "query",
            ""
        )

        results, has_next = await search_movies(
            query=query,
            page=0,
            filters_data={}
        )

        text = build_search_text(
            query=query,
            results=results,
            page=0,
            has_next=has_next,
            filters_data={}
        )

        keyboard = search_result_buttons(
            results=results,
            session_id=session_id,
            page=0,
            has_next=has_next
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except MessageNotModified:

            pass

        except Exception as e:

            logger.error(
                "CLEAR FILTER ERROR: %s",
                e,
                exc_info=True
            )

        await callback.answer(
            "Filters cleared."
        )
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # FILTER BACK
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^filterback_[a-fA-F0-9]+$"
        )
    )
    async def filter_back_callback(
        client,
        callback
    ):

        session_id = callback.data.split(
            "_",
            1
        )[1]

        user_id = callback.from_user.id

        session = await get_search_session(
            session_id,
            user_id
        )

        if not session:

            await callback.answer(
                "Search expired.",
                show_alert=True
            )

            return

        query = session.get(
            "query",
            ""
        )

        filters_data = session.get(
            "filters",
            {}
        ) or {}

        results, has_next = await search_movies(
            query=query,
            page=0,
            filters_data=filters_data
        )

        text = build_search_text(
            query=query,
            results=results,
            page=0,
            has_next=has_next,
            filters_data=filters_data
        )

        keyboard = search_result_buttons(
            results=results,
            session_id=session_id,
            page=0,
            has_next=has_next
        )

        try:

            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except MessageNotModified:

            pass

        except Exception as e:

            logger.error(
                "FILTER BACK ERROR: %s",
                e,
                exc_info=True
            )

        await callback.answer()
        
# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    # ========================================================
    # CLOSE SEARCH
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^search_close_[a-fA-F0-9]+$"
        )
    )
    async def search_close_callback(
        client,
        callback
    ):

        session_id = callback.data.split(
            "_",
            2
        )[2]

        try:

            await delete_search_session(
                session_id
            )

        except Exception:

            pass

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

    # ========================================================
    # NO-OP
    # ========================================================

    @app.on_callback_query(
        filters.regex(
            r"^noop$"
        )
    )
    async def noop_callback(
        client,
        callback
    ):

        await callback.answer()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
