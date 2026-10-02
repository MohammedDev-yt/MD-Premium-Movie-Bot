# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import re
from datetime import datetime, timezone

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def is_media_message(message):
    """
    Check whether a Telegram message contains supported media.
    """

    return bool(
        message
        and (
            message.document
            or message.video
            or message.audio
            or message.animation
        )
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_original_filename(message):
    """
    Get the original filename from Telegram media.
    """

    if not message:
        return None

    if message.document:
        return message.document.file_name

    if message.video:
        return message.video.file_name

    if message.audio:
        return message.audio.file_name

    if message.animation:
        return message.animation.file_name

    return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def remove_extension(filename):
    """
    Remove the file extension.
    """

    if not filename:
        return ""

    return re.sub(
        r"\.(mkv|mp4|avi|mov|webm|flv|wmv|mp3|m4a|aac|ogg|wav|zip|rar|7z)$",
        "",
        filename,
        flags=re.IGNORECASE
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def clean_title(text):
    """
    Clean filename/caption and produce a searchable movie/series title.
    """

    if not text:
        return ""

    text = remove_extension(text)

    # Remove common separators
    text = re.sub(r"[_\.]+", " ", text)

    # Remove season / episode patterns
    text = re.sub(
        r"\bS\d{1,2}\s*E\d{1,3}\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bSeason\s*\d{1,2}\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"\bEpisode\s*\d{1,3}\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove resolutions
    text = re.sub(
        r"\b(?:360p|480p|576p|720p|1080p|1440p|2160p|4k|8k)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove common quality/source tags
    text = re.sub(
        r"\b(?:WEB[- ]?DL|WEB[- ]?RIP|WEB|HDRIP|HDTV|DVDRIP|BRRIP|BLURAY|BDRIP|CAMRIP|CAM|TELESYNC|TS|TC|SCR|DVD)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove codecs
    text = re.sub(
        r"\b(?:x264|x265|h264|h265|hevc|avc|10bit|8bit)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove common audio tags
    text = re.sub(
        r"\b(?:AAC|AC3|DDP|DD|DTS|TRUEHD|ATMOS|MP3|EAC3|5\.1|7\.1)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove common release/source tags
    text = re.sub(
        r"\b(?:PROPER|REMASTERED|UNCUT|EXTENDED|UNRATED|DIRECTORS?\s*CUT|IMAX)\b",
        " ",
        text,
        flags=re.IGNORECASE
    )

    # Remove brackets
    text = re.sub(r"[\[\]\(\)\{\}]", " ", text)

    # Clean multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_message_title(message):
    """
    Get the best title from filename or caption.
    """

    filename = get_original_filename(message)

    if filename:
        title = clean_title(filename)

        if title:
            return title

    caption = getattr(message, "caption", None)

    if caption:
        first_line = caption.split("\n")[0].strip()

        title = clean_title(first_line)

        if title:
            return title

    return "Untitled Media"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def normalize_search_text(text):
    """
    Normalize text for searching.
    """

    if not text:
        return ""

    text = text.lower()

    text = re.sub(r"[_\.\-]+", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def get_search_key(text):
    """
    Generate normalized search key.
    """

    return normalize_search_text(
        clean_title(text)
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

SUPPORTED_LANGUAGES = [
    "Hindi",
    "English",
    "Tamil",
    "Telugu",
    "Malayalam",
    "Kannada",
    "Bengali",
    "Marathi",
    "Gujarati",
    "Punjabi",
    "Urdu",
    "Odia",
    "Assamese",
    "Nepali",
    "Bhojpuri",
    "Korean",
    "Japanese",
    "Chinese",
    "Spanish",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Russian",
    "Arabic",
    "Turkish",
    "Thai",
    "Indonesian",
    "Vietnamese",
    "English + Hindi",
    "Hindi + English",
    "Dual Audio",
    "Multi Audio",
    "Multi"
]

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_language(text):
    """
    Extract language from filename/caption.

    Examples:
        Movie Name Hindi 1080p
        Movie Name [Hindi]
        Movie Name - English
        Movie Name Hindi + English
    """

    if not text:
        return None

    text_lower = text.lower()

    # Check combined language names first
    combined_patterns = [
        (
            r"\bhindi\s*(?:\+|&|and|[-/])\s*english\b",
            "Hindi + English"
        ),
        (
            r"\benglish\s*(?:\+|&|and|[-/])\s*hindi\b",
            "English + Hindi"
        ),
        (
            r"\bdual[\s_-]*audio\b",
            "Dual Audio"
        ),
        (
            r"\bmulti[\s_-]*audio\b",
            "Multi Audio"
        ),
    ]

    for pattern, language in combined_patterns:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return language

    # Check individual languages
    for language in SUPPORTED_LANGUAGES:
        # Skip combined values
        if "+" in language or language in (
            "Dual Audio",
            "Multi Audio",
            "Multi"
        ):
            continue

        pattern = rf"(?<![a-z]){re.escape(language.lower())}(?![a-z])"

        if re.search(pattern, text_lower, re.IGNORECASE):
            return language

    return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_year(text):
    """
    Extract a valid year between 1960 and 2026.

    Examples:
        Iron Man 2008 Hindi
        Movie (2019)
        Movie [2024]
    """

    if not text:
        return None

    matches = re.findall(
        r"(?<!\d)(19[6-9]\d|20[0-2]\d)(?!\d)",
        text
    )

    for year in matches:
        year = int(year)

        if 1960 <= year <= 2026:
            return year

    return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_season(text):
    """
    Extract season number from filename/caption.

    Supported examples:

        S01
        S1
        S02E03
        Season 2
        Season02
        Season 02
    """

    if not text:
        return None

    patterns = [
        r"\bS(?:EASON)?\s*[-._ ]?(\d{1,2})\b",
        r"\bSEASON\s*[-._ ]?(\d{1,2})\b",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        if match:
            season = int(match.group(1))

            if 1 <= season <= 20:
                return season

    return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_episode(text):
    """
    Extract episode number from filename/caption.

    Supported examples:

        S01E01
        S1E5
        E03
        Episode 10
        Ep 25
        Episode.50
    """

    if not text:
        return None

    # S01E03 / S1E3
    match = re.search(
        r"\bS\d{1,2}\s*E(\d{1,3})\b",
        text,
        flags=re.IGNORECASE
    )

    if match:
        episode = int(match.group(1))

        if 1 <= episode <= 50:
            return episode

    # Episode 03 / Episode.03 / Episode-03
    match = re.search(
        r"\bEPISODE\s*[-._ ]?(\d{1,3})\b",
        text,
        flags=re.IGNORECASE
    )

    if match:
        episode = int(match.group(1))

        if 1 <= episode <= 50:
            return episode

    # Ep 03
    match = re.search(
        r"\bEP\s*[-._ ]?(\d{1,3})\b",
        text,
        flags=re.IGNORECASE
    )

    if match:
        episode = int(match.group(1))

        if 1 <= episode <= 50:
            return episode

    # Standalone E03
    match = re.search(
        r"(?<![A-Z])E\s*[-._ ]?(\d{1,3})\b",
        text,
        flags=re.IGNORECASE
    )

    if match:
        episode = int(match.group(1))

        if 1 <= episode <= 50:
            return episode

    return None

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def extract_media_metadata(text):
    """
    Extract language, year, season and episode together.

    Returns:
        {
            "language": "...",
            "year": 2024,
            "season": 2,
            "episode": 3
        }
    """

    return {
        "language": extract_language(text),
        "year": extract_year(text),
        "season": extract_season(text),
        "episode": extract_episode(text),
    }

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def human_size(size):
    """
    Convert bytes into readable size.
    """

    if size is None:
        return "0 B"

    try:
        size = float(size)
    except (TypeError, ValueError):
        return "0 B"

    units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB",
    ]

    index = 0

    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1

    if index == 0:
        return f"{int(size)} {units[index]}"

    return f"{size:.2f} {units[index]}"

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def shorten(text, max_length=50):
    """
    Shorten long text.
    """

    if not text:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    return text[:max_length - 3] + "..."

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def escape_html(text):
    """
    Escape HTML characters safely.
    """

    if text is None:
        return ""

    text = str(text)

    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

def utc_now():
    """
    Return current UTC datetime.
    """

    return datetime.now(timezone.utc)