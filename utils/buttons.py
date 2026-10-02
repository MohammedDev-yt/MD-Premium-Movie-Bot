# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import re
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# SEARCH RESULT FORMAT HELPERS
# ============================================================

def format_file_size(size):
    """
    Convert bytes into MB / GB.
    Example:
    734003200  -> 700 MB
    2976417792 -> 2.77 GB
    """

    try:
        size = float(size)
    except (TypeError, ValueError):
        return "Unknown Size"

    if size <= 0:
        return "Unknown Size"

    mb = size / (1024 ** 2)

    if mb >= 1024:
        gb = size / (1024 ** 3)
        return f"{gb:.2f} GB"

    return f"{mb:.0f} MB"


def detect_quality(text):
    """
    Detect quality from title / filename.

    Examples:
    480p
    720p
    1080p
    1440p
    2160p
    4K
    """

    if not text:
        return "Unknown"

    text = str(text)

    match = re.search(
        r'(?<!\d)(2160p|1440p|1080p|720p|576p|480p|360p)(?!\d)',
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).lower()

    # Detect 4K
    if re.search(r'(?<![a-z0-9])4k(?![a-z0-9])', text, re.IGNORECASE):
        return "4K"

    return "Unknown"

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
    has_next=False,
    bot_username=None,
    total_pages=None,
):
    buttons = []

    if total_pages is not None:
        try:
            has_next = int(page) + 1 < int(total_pages)
        except Exception:
            pass

    for result in results:

        message_id = (
            result.get("message_id")
            or result.get("telegram_message_id")
            or result.get("msg_id")
        )

        if not message_id:
            continue

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = (
            result.get("title")
            or result.get("file_name")
            or result.get("filename")
            or result.get("name")
            or "Unknown File"
        )

        title = str(title).strip()

        title = re.sub(
            r"^\s*\d+\.\s*",
            "",
            title,
        )

        # ----------------------------------------------------
        # FILE SIZE
        # ----------------------------------------------------

        file_size = (
            result.get("file_size")
            or result.get("size")
            or result.get("file_size_bytes")
            or 0
        )

        size_text = format_file_size(file_size)

        # ----------------------------------------------------
        # QUALITY
        # ----------------------------------------------------

        quality = (
            result.get("quality")
            or result.get("resolution")
        )

        if quality:
            quality = str(quality).strip()
        else:
            quality = detect_quality(title)

        button_title = title

        if len(button_title) > 55:
            button_title = button_title[:52] + "..."

        button_text = (
            f"[{size_text}] | "
            f"[{quality}] | "
            f"{button_title}"
        )

        # ----------------------------------------------------
        # DEEP LINK
        # ----------------------------------------------------

        if bot_username:

            username = str(
                bot_username
            ).lstrip("@")

            url = (
                f"https://t.me/{username}"
                f"?start=file_{int(message_id)}"
            )

            buttons.append([
                InlineKeyboardButton(
                    f"›› {button_text}",
                    url=url,
                )
            ])

        else:

            buttons.append([
                InlineKeyboardButton(
                    f"›› {button_text}",
                    callback_data=(
                        f"file_{int(message_id)}"
                    ),
                )
            ])

    # --------------------------------------------------------
    # SEND ALL
    # --------------------------------------------------------

    if results:

        if bot_username:

            username = str(
                bot_username
            ).lstrip("@")

            sendall_url = (
                f"https://t.me/{username}"
                f"?start=sendall_{session_id}_{page}"
            )

            send_all_button = InlineKeyboardButton(
                "Sᴇɴᴅ Aʟʟ",
                url=sendall_url,
            )

        else:

            send_all_button = InlineKeyboardButton(
                "Sᴇɴᴅ Aʟʟ",
                callback_data=(
                    f"sendall_{session_id}_{page}"
                ),
            )

    else:

        send_all_button = None

    # --------------------------------------------------------
    # FILTER BUTTONS
    # --------------------------------------------------------

    # SEND ALL
    if send_all_button:

        buttons.append([
            send_all_button
        ])

    # FILTERS
    buttons.append([
        InlineKeyboardButton(
            "Lᴀɴɢᴜᴀɢᴇs",
            callback_data=(
                f"filter_lang_{session_id}_{page}"
            ),
        ),

        InlineKeyboardButton(
            "Eᴘɪsᴏᴅᴇs",
            callback_data=(
                f"filter_episode_{session_id}_{page}"
            ),
        ),

        InlineKeyboardButton(
            "Sᴇᴀsᴏɴs",
            callback_data=(
                f"filter_season_{session_id}_{page}"
            ),
        ),
    ])
    
    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    navigation = []

    if page > 0:

        navigation.append(
            InlineKeyboardButton(
                "‹ ʙᴀᴄᴋ",
                callback_data=(
                    f"page_{session_id}_{page - 1}"
                ),
            )
        )

    if has_next:

        navigation.append(
            InlineKeyboardButton(
                "ɴᴇxᴛ ›",
                callback_data=(
                    f"page_{session_id}_{page + 1}"
                ),
            )
        )

    if navigation:
        buttons.append(navigation)

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def filter_menu_buttons(
    session_id,
    page=0,
    available=None,
):
    available = available or {}

    languages = available.get(
        "languages",
        [],
    )

    years = available.get(
        "years",
        [],
    )

    qualities = available.get(
        "qualities",
        [],
    )

    seasons = available.get(
        "seasons",
        [],
    )

    episodes = available.get(
        "episodes",
        [],
    )

    buttons = []

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    if languages:

        buttons.append([
            InlineKeyboardButton(
                "🌐 Lᴀɴɢᴜᴀɢᴇ",
                callback_data=(
                    f"filter_lang_{session_id}_{page}"
                ),
            )
        ])

    # --------------------------------------------------------
    # SEASON
    # --------------------------------------------------------

    if seasons:

        buttons.append([
            InlineKeyboardButton(
                "📺 Sᴇᴀsᴏɴ",
                callback_data=(
                    f"filter_season_{session_id}_{page}"
                ),
            )
        ])

    # --------------------------------------------------------
    # EPISODE
    # --------------------------------------------------------

    if episodes:

        buttons.append([
            InlineKeyboardButton(
                "🎬 Eᴘɪsᴏᴅᴇ",
                callback_data=(
                    f"filter_episode_{session_id}_{page}"
                ),
            )
        ])

    # --------------------------------------------------------
    # CLEAR ALL
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Cʟᴇᴀʀ Fɪʟᴛᴇʀs",
            callback_data=(
                f"filter_clear_{session_id}_{page}"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_{session_id}_{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def language_filter_buttons(
    session_id,
    languages,
    page=0,
    current_language=None,
):
    buttons = []

    languages = languages or []

    row = []

    for language in languages:

        language = str(
            language
        ).strip()

        if not language:
            continue

        text = (
            f"✓ {language}"
            if current_language
            and str(current_language).lower()
            == language.lower()
            else language
        )

        callback_value = language[:25]

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=(
                    f"setlang_"
                    f"{session_id}_"
                    f"{page}_"
                    f"{callback_value}"
                ),
            )
        )

        if len(row) == 2:

            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "• Close •",
            callback_data=(
                f"setlang_"
                f"{session_id}_"
                f"{page}_clear"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def year_filter_buttons(
    session_id,
    years,
    page=0,
    current_year=None,
):
    buttons = []

    years = years or []

    try:

        years = sorted(
            {
                int(year)
                for year in years
            },
            reverse=True,
        )

    except Exception:
        pass

    row = []

    for year in years:

        try:
            year_int = int(year)
        except Exception:
            continue

        if not 1960 <= year_int <= 2026:
            continue

        try:

            is_current = (
                current_year is not None
                and int(current_year)
                == year_int
            )

        except Exception:

            is_current = False

        text = (
            f"✓ {year_int}"
            if is_current
            else str(year_int)
        )

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=(
                    f"setyear_"
                    f"{session_id}_"
                    f"{page}_"
                    f"{year_int}"
                ),
            )
        )

        if len(row) == 3:

            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Clear Year",
            callback_data=(
                f"setyear_"
                f"{session_id}_"
                f"{page}_clear"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def quality_filter_buttons(
    session_id,
    qualities,
    page=0,
    current_quality=None,
):
    buttons = []

    qualities = qualities or []

    row = []

    for quality in qualities:

        quality = str(
            quality
        ).strip()

        if not quality:
            continue

        is_current = (
            current_quality
            and str(current_quality).lower()
            == quality.lower()
        )

        text = (
            f"✓ {quality}"
            if is_current
            else quality
        )

        value = quality[:20]

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=(
                    f"setquality_"
                    f"{session_id}_"
                    f"{page}_"
                    f"{value}"
                ),
            )
        )

        if len(row) == 2:

            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # --------------------------------------------------------
    # CLEAR QUALITY
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Clear Quality",
            callback_data=(
                f"setquality_"
                f"{session_id}_"
                f"{page}_clear"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def season_filter_buttons(
    session_id,
    seasons,
    page=0,
    current_season=None,
):
    buttons = []

    seasons = seasons or []

    try:

        seasons = sorted(
            {
                int(season)
                for season in seasons
            }
        )

    except Exception:
        pass

    row = []

    for season in seasons:

        try:
            season_int = int(season)
        except Exception:
            continue

        if not 1 <= season_int <= 20:
            continue

        try:

            is_current = (
                current_season is not None
                and int(current_season)
                == season_int
            )

        except Exception:

            is_current = False

        text = (
            f"✓ S{season_int:02d}"
            if is_current
            else f"S{season_int:02d}"
        )

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=(
                    f"setseason_"
                    f"{session_id}_"
                    f"{page}_"
                    f"{season_int}"
                ),
            )
        )

        if len(row) == 4:

            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Clear Season",
            callback_data=(
                f"setseason_"
                f"{session_id}_"
                f"{page}_clear"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def episode_filter_buttons(
    session_id,
    episodes,
    page=0,
    current_episode=None,
):
    buttons = []

    episodes = episodes or []

    try:

        episodes = sorted(
            {
                int(episode)
                for episode in episodes
            }
        )

    except Exception:
        pass

    row = []

    for episode in episodes:

        try:
            episode_int = int(episode)
        except Exception:
            continue

        if not 1 <= episode_int <= 50:
            continue

        try:

            is_current = (
                current_episode is not None
                and int(current_episode)
                == episode_int
            )

        except Exception:

            is_current = False

        text = (
            f"✓ E{episode_int:02d}"
            if is_current
            else f"E{episode_int:02d}"
        )

        row.append(
            InlineKeyboardButton(
                text,
                callback_data=(
                    f"setepisode_"
                    f"{session_id}_"
                    f"{page}_"
                    f"{episode_int}"
                ),
            )
        )

        if len(row) == 5:

            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    # --------------------------------------------------------
    # CLEAR
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Clear Episode",
            callback_data=(
                f"setepisode_"
                f"{session_id}_"
                f"{page}_clear"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def active_filter_buttons(
    session_id,
    page=0,
    filters=None,
):
    filters = filters or {}

    buttons = []

    language = filters.get(
        "language"
    )

    year = filters.get(
        "year"
    )

    quality = filters.get(
        "quality"
    )

    season = filters.get(
        "season"
    )

    episode = filters.get(
        "episode"
    )

    if language:

        buttons.append([
            InlineKeyboardButton(
                f"🌐 {language}",
                callback_data=(
                    f"setlang_"
                    f"{session_id}_"
                    f"{page}_clear"
                ),
            )
        ])

    if year:

        buttons.append([
            InlineKeyboardButton(
                f"📅 {year}",
                callback_data=(
                    f"setyear_"
                    f"{session_id}_"
                    f"{page}_clear"
                ),
            )
        ])

    if quality:

        buttons.append([
            InlineKeyboardButton(
                f"🎞 {quality}",
                callback_data=(
                    f"setquality_"
                    f"{session_id}_"
                    f"{page}_clear"
                ),
            )
        ])

    if season:

        buttons.append([
            InlineKeyboardButton(
                f"📺 S{int(season):02d}",
                callback_data=(
                    f"setseason_"
                    f"{session_id}_"
                    f"{page}_clear"
                ),
            )
        ])

    if episode:

        buttons.append([
            InlineKeyboardButton(
                f"🎬 E{int(episode):02d}",
                callback_data=(
                    f"setepisode_"
                    f"{session_id}_"
                    f"{page}_clear"
                ),
            )
        ])

    # --------------------------------------------------------
    # CLEAR ALL
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "✖️ Cʟᴇᴀʀ Aʟʟ",
            callback_data=(
                f"filter_clear_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    # --------------------------------------------------------
    # BACK
    # --------------------------------------------------------

    buttons.append([
        InlineKeyboardButton(
            "‹ Bᴀᴄᴋ",
            callback_data=(
                f"filter_back_"
                f"{session_id}_"
                f"{page}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def premium_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💎 Gᴇᴛ Pʀᴇᴍɪᴜᴍ",
                callback_data="premium_plans",
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Rᴇᴅᴇᴇᴍ Cᴏᴅᴇ",
                callback_data="redeem",
            )
        ],
        [
            InlineKeyboardButton(
                "‹ Bᴀᴄᴋ",
                callback_data="close",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def plan_confirm_buttons(amount):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "💳 Pᴀʏ Nᴏᴡ",
                callback_data=f"pay_{amount}",
            )
        ],
        [
            InlineKeyboardButton(
                "‹ Bᴀᴄᴋ Tᴏ Pʟᴀɴs",
                callback_data="premium",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def file_sent_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "• Uᴘᴅᴀᴛᴇs •",
                url="https://t.me/Aero_Unity",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def open_bot_button(
    bot_username,
    start_parameter=None,
):
    username = str(
        bot_username
    ).lstrip("@")

    if start_parameter:

        url = (
            f"https://t.me/{username}"
            f"?start={start_parameter}"
        )

    else:

        url = (
            f"https://t.me/{username}"
        )

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🤖 Oᴘᴇɴ Bᴏᴛ",
                url=url,
            )
        ]
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def open_bot_close_buttons(
    bot_username,
    start_parameter=None,
):
    username = str(
        bot_username
    ).lstrip("@")

    if start_parameter:

        url = (
            f"https://t.me/{username}"
            f"?start={start_parameter}"
        )

    else:

        url = (
            f"https://t.me/{username}"
        )

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🤖 Oᴘᴇɴ Bᴏᴛ",
                url=url,
            )
        ],
        [
            InlineKeyboardButton(
                "• Cʟᴏsᴇ •",
                callback_data="close",
            )
        ],
    ])

def close_button():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "• Cʟᴏsᴇ •",
                callback_data="close",
            )
        ]
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def back_button(
    callback_data="close",
):

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "‹ Bᴀᴄᴋ",
                callback_data=callback_data,
            )
        ]
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def account_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "👤 Mʏ Aᴄᴄᴏᴜɴᴛ",
                callback_data="account",
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Pʀᴇᴍɪᴜᴍ",
                callback_data="premium",
            )
        ],
        [
            InlineKeyboardButton(
                "‹ Bᴀᴄᴋ",
                callback_data="close",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# HELP BUTTONS
# ============================================================

def help_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                " Hᴏᴡ Tᴏ Uѕᴇ",
                callback_data="help_usage",
            )
        ],
        [
            InlineKeyboardButton(
                " Sᴇᴀʀᴄʜ Hᴇʟᴘ",
                callback_data="help_search",
            )
        ],
        [
            InlineKeyboardButton(
                " Pʀᴇᴍɪᴜᴍ",
                callback_data="premium",
            )
        ],
        [
            InlineKeyboardButton(
                "‹ Bᴀᴄᴋ",
                callback_data="close",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

# ============================================================
# HOME BUTTONS
# ============================================================

def home_buttons():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "• Sᴇᴀʀᴄh •",
                callback_data="search",
            ),
            InlineKeyboardButton(
                "• Pʀᴇᴍɪᴜᴍ •",
                callback_data="premium",
            ),
        ],
        [
            InlineKeyboardButton(
                "• Uᴘᴅᴀᴛᴇs •",
                url="https://t.me/Aero_Unity",
            )
        ],
    ])

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def fsub_channel_button(
    channel_name,
    channel_url,
):
    return InlineKeyboardButton(
        f"›› {channel_name}",
        url=channel_url,
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def fsub_try_again_button(
    deep_link,
):
    return InlineKeyboardButton(
        "• Tʀʏ Aɢᴀɪɴ •",
        callback_data=(
            f"fsub_check_{deep_link}"
        ),
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def fsub_close_button():

    return InlineKeyboardButton(
        "• Cʟᴏsᴇ •",
        callback_data="fsub_close",
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def force_sub_buttons(
    channels=None,
    deep_link=None,
):
    buttons = []

    channels = channels or []

    for channel in channels:

        if isinstance(
            channel,
            dict,
        ):

            name = (
                channel.get("name")
                or channel.get("title")
                or channel.get("username")
                or "Join Channel"
            )

            url = (
                channel.get("url")
                or channel.get("invite_link")
                or channel.get("link")
            )

            if url:

                buttons.append([
                    fsub_channel_button(
                        name,
                        url,
                    )
                ])

        elif isinstance(
            channel,
            (list, tuple),
        ):

            if len(channel) >= 2:

                buttons.append([
                    fsub_channel_button(
                        str(channel[0]),
                        str(channel[1]),
                    )
                ])

    if deep_link:

        buttons.append([
            fsub_try_again_button(
                deep_link
            )
        ])

    buttons.append([
        fsub_close_button()
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def pagination_buttons(
    session_id,
    page=0,
    has_next=False,
):
    buttons = []

    row = []

    if page > 0:

        row.append(
            InlineKeyboardButton(
                "‹",
                callback_data=(
                    f"page_"
                    f"{session_id}_"
                    f"{page - 1}"
                ),
            )
        )

    row.append(
        InlineKeyboardButton(
            f"• {page + 1} •",
            callback_data="noop",
        )
    )

    if has_next:

        row.append(
            InlineKeyboardButton(
                "›",
                callback_data=(
                    f"page_"
                    f"{session_id}_"
                    f"{page + 1}"
                ),
            )
        )

    buttons.append(row)

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def filter_page_buttons(
    session_id,
    page=0,
    has_next=False,
):
    buttons = []

    row = []

    if page > 0:

        row.append(
            InlineKeyboardButton(
                "‹",
                callback_data=(
                    f"page_"
                    f"{session_id}_"
                    f"{page - 1}"
                ),
            )
        )

    if has_next:

        row.append(
            InlineKeyboardButton(
                "›",
                callback_data=(
                    f"page_"
                    f"{session_id}_"
                    f"{page + 1}"
                ),
            )
        )

    if row:
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            "• Fɪʟᴛᴇʀs •",
            callback_data=(
                f"filter_menu_"
                f"{session_id}"
            ),
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def no_results_buttons(
    bot_username=None,
):
    buttons = []

    if bot_username:

        username = str(
            bot_username
        ).lstrip("@")

        buttons.append([
            InlineKeyboardButton(
                "• Sᴇᴀʀᴄʜ Aɢᴀɪɴ •",
                url=(
                    f"https://t.me/{username}"
                ),
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            "• Uᴘᴅᴀᴛᴇs •",
            url="https://t.me/Aero_Unity",
        )
    ])

    return InlineKeyboardMarkup(buttons)

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def noop_button(
    text="•",
):

    return InlineKeyboardButton(
        text,
        callback_data="noop",
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
