# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

import logging
import re
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

from config import (
    MONGO_URI,
    DB_NAME,
    FREE_REQUESTS,
    STORAGE_LIMIT_MB
)

logger = logging.getLogger(__name__)

async def ensure_index(
    collection,
    keys,
    name=None,
    unique=False
):
    """
    Create an index only if the same key pattern
    does not already exist.

    Prevents MongoDB IndexOptionsConflict errors
    when an index already exists with another name.
    """

    try:

        existing_indexes = (
            await collection.index_information()
        )

        # ----------------------------------------------------
        # CHECK EXISTING INDEXES
        # ----------------------------------------------------

        for index_name, index_info in existing_indexes.items():

            existing_keys = list(
                index_info.get(
                    "key",
                    []
                )
            )

            if existing_keys == keys:

                return index_name

        # ----------------------------------------------------
        # CREATE NEW INDEX
        # ----------------------------------------------------

        kwargs = {
            "unique": unique
        }

        if name:
            kwargs["name"] = name

        return await collection.create_index(
            keys,
            **kwargs
        )

    except Exception as e:

        logger.warning(
            "Index check failed for %s: %s",
            name or keys,
            e
        )

        return None

# ============================================================
# MONGODB CONNECTION
# ============================================================

mongo_client = None
db = None

users_collection = None
media_collection = None
search_sessions_collection = None
settings_collection = None
chats_collection = None
redeem_codes_collection = None
banned_users_collection = None
admins_collection = None

# ============================================================
# CONNECT
# ============================================================

async def init_database():

    global mongo_client
    global db
    global users_collection
    global media_collection
    global search_sessions_collection
    global settings_collection
    global chats_collection
    global redeem_codes_collection
    global banned_users_collection
    global admins_collection

    if not MONGO_URI:

        raise RuntimeError(
            "MONGO_URI is not configured."
        )

    mongo_client = AsyncIOMotorClient(
        MONGO_URI,
        serverSelectionTimeoutMS=10000
    )

    await mongo_client.admin.command(
        "ping"
    )

    db = mongo_client[
        DB_NAME
    ]

    users_collection = db[
        "users"
    ]

    media_collection = db[
        "media"
    ]

    search_sessions_collection = db[
        "search_sessions"
    ]

    settings_collection = db[
        "settings"
    ]

    chats_collection = db[
        "chats"
    ]

    redeem_codes_collection = db[
        "redeem_codes"
    ]

    banned_users_collection = db[
        "banned_users"
    ]
    
    admins_collection = db[
        "admins"
    ]

        # ========================================================
    # DATABASE INDEXES
    # ========================================================

    # --------------------------------------------------------
    # USER
    # --------------------------------------------------------

    await ensure_index(
        users_collection,
        [("user_id", 1)],
        name="user_id",
        unique=True
    )

    # --------------------------------------------------------
    # CHAT
    # --------------------------------------------------------

    await ensure_index(
        chats_collection,
        [("chat_id", 1)],
        name="chat_id",
        unique=True
    )

    # --------------------------------------------------------
    # MEDIA
    # --------------------------------------------------------

    await ensure_index(
        media_collection,
        [("message_id", 1)],
        name="message_id"
    )

    await ensure_index(
        media_collection,
        [("title_key", 1)],
        name="title_key"
    )

    await ensure_index(
        media_collection,
        [("search_key", 1)],
        name="search_key"
    )

    await ensure_index(
        media_collection,
        [("file_name", 1)],
        name="file_name"
    )

    await ensure_index(
        media_collection,
        [("filename", 1)],
        name="filename"
    )

    await ensure_index(
        media_collection,
        [("language", 1)],
        name="language"
    )

    await ensure_index(
        media_collection,
        [("year", 1)],
        name="year"
    )

    await ensure_index(
        media_collection,
        [("season", 1)],
        name="season"
    )

    await ensure_index(
        media_collection,
        [("episode", 1)],
        name="episode"
    )

    await ensure_index(
        media_collection,
        [("quality", 1)],
        name="quality"
    )

    await ensure_index(
        media_collection,
        [
            ("channel_id", 1),
            ("message_id", 1)
        ],
        name="channel_id_message_id",
        unique=True
    )

    # --------------------------------------------------------
    # SEARCH SESSIONS
    # --------------------------------------------------------

    await ensure_index(
        search_sessions_collection,
        [("session_id", 1)],
        name="session_id",
        unique=True
    )

    await ensure_index(
        search_sessions_collection,
        [("user_id", 1)],
        name="search_user_id"
    )

    # --------------------------------------------------------
    # REDEEM
    # --------------------------------------------------------

    await ensure_index(
        redeem_codes_collection,
        [("code", 1)],
        name="code",
        unique=True
    )

    # --------------------------------------------------------
    # BANNED USERS
    # --------------------------------------------------------

    await ensure_index(
        banned_users_collection,
        [("user_id", 1)],
        name="banned_user_id",
        unique=True
    )

    logger.info(
        "MongoDB connected successfully."
    )

    logger.info(
        "MongoDB indexes ready."
    )
    
    # --------------------------------------------------------
    # ADMINS
    # --------------------------------------------------------

    await ensure_index(
        admins_collection,
        [("user_id", 1)],
        name="admin_user_id",
        unique=True
    )

# ============================================================
# CLOSE
# ============================================================

async def close_database():

    global mongo_client

    if mongo_client:

        mongo_client.close()

        mongo_client = None

        logger.info(
            "MongoDB connection closed."
        )

# ============================================================
# USER
# ============================================================

async def create_user(
    user_id,
    first_name="",
    username=""
):

    now = datetime.utcnow()

    first_name = (
        first_name or ""
    )

    username = (
        username or ""
    )

    await users_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {
                "first_name": first_name,
                "username": username,
                "updated_at": now
            },

            "$setOnInsert": {

                "user_id": user_id,

                "premium": False,

                "plan": None,

                "paid_amount": 0,

                "premium_requests": 0,

                "remaining_requests":
                    FREE_REQUESTS,

                "total_requests_used": 0,

                "tokens": 0,

                "last_token_claim": None,

                "created_at": now
            }
        },

        upsert=True
    )

    return await get_user(
        user_id
    )


async def get_user(
    user_id
):

    return await users_collection.find_one(
        {
            "user_id": user_id
        }
    )


async def get_or_create_user(
    user_id,
    first_name="",
    username=""
):

    user = await get_user(
        user_id
    )

    if user:

        return user

    return await create_user(
        user_id=user_id,
        first_name=first_name,
        username=username
    )


async def update_user(
    user_id,
    first_name=None,
    username=None
):

    update = {
        "updated_at":
            datetime.utcnow()
    }

    if first_name is not None:

        update["first_name"] = (
            first_name
        )

    if username is not None:

        update["username"] = (
            username
        )

    await users_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": update
        }
    )

# ============================================================
# TOKEN SYSTEM
# ============================================================

async def get_token_balance(
    user_id
):

    user = await users_collection.find_one(

        {
            "user_id": user_id
        },

        {
            "_id": 0,
            "tokens": 1
        }
    )

    if not user:
        return 0

    return int(
        user.get(
            "tokens",
            0
        ) or 0
    )

# ============================================================
# DAILY TOKENS
# ============================================================

async def claim_daily_tokens(
    user_id
):

    now = datetime.utcnow()

    user = await get_user(
        user_id
    )

    if not user:

        return {
            "success": False,
            "reason": "user_not_found",
            "tokens": 0
        }

    last_claim = user.get(
        "last_token_claim"
    )

    if last_claim:

        if last_claim.date() == now.date():

            return {
                "success": False,
                "reason": "already_claimed",
                "tokens": int(
                    user.get(
                        "tokens",
                        0
                    ) or 0
                )
            }

    start_of_day = datetime(
        now.year,
        now.month,
        now.day
    )

    result = await users_collection.find_one_and_update(

        {
            "user_id": user_id,

            "$or": [

                {
                    "last_token_claim": None
                },

                {
                    "last_token_claim": {
                        "$exists": False
                    }
                },

                {
                    "last_token_claim": {
                        "$lt": start_of_day
                    }
                }
            ]
        },

        {
            "$inc": {
                "tokens": 50
            },

            "$set": {
                "last_token_claim": now,
                "updated_at": now
            }
        },

        return_document=ReturnDocument.AFTER
    )

    if not result:

        current = await get_token_balance(
            user_id
        )

        return {
            "success": False,
            "reason": "already_claimed",
            "tokens": current
        }

    return {
        "success": True,
        "reason": "claimed",
        "tokens": int(
            result.get(
                "tokens",
                0
            ) or 0
        )
    }

# ============================================================
# TOKEN → PREMIUM
# ============================================================

async def redeem_tokens_for_premium(
    user_id,
    token_cost,
    plan_name,
    requests
):

    now = datetime.utcnow()

    try:
        token_cost = int(token_cost)
        requests = int(requests)
    except (
        TypeError,
        ValueError
    ):
        return {
            "success": False,
            "reason": "invalid_plan",
            "tokens": await get_token_balance(user_id)
        }

    if token_cost <= 0 or requests <= 0:

        return {
            "success": False,
            "reason": "invalid_plan",
            "tokens": await get_token_balance(user_id)
        }

    result = await users_collection.find_one_and_update(

        {
            "user_id": user_id,

            "tokens": {
                "$gte": token_cost
            }
        },

        {
            "$inc": {
                "tokens": -token_cost
            },

            "$set": {

                "premium": True,

                "plan": plan_name,

                "paid_amount": 0,

                "premium_requests": requests,

                "remaining_requests": requests,

                "updated_at": now
            }
        },

        return_document=ReturnDocument.AFTER
    )

    # --------------------------------------------------------
    # FAILED
    # --------------------------------------------------------

    if not result:

        current = await get_user(
            user_id
        )

        if not current:

            return {
                "success": False,
                "reason": "user_not_found",
                "tokens": 0
            }

        return {
            "success": False,
            "reason": "insufficient_tokens",
            "tokens": int(
                current.get(
                    "tokens",
                    0
                ) or 0
            )
        }

    # --------------------------------------------------------
    # SUCCESS
    # --------------------------------------------------------

    return {

        "success": True,

        "reason": "redeemed",

        "tokens": int(
            result.get(
                "tokens",
                0
            ) or 0
        ),

        "plan":
            result.get(
                "plan",
                plan_name
            ),

        "requests":
            int(
                result.get(
                    "premium_requests",
                    requests
                ) or requests
            )
    }

# ============================================================
# CHAT
# ============================================================

async def register_chat(
    chat_id,
    chat_type=None,
    title=None
):

    if chat_id is None:
        return False

    now = datetime.utcnow()

    await chats_collection.update_one(

        {
            "chat_id": chat_id
        },

        {
            "$set": {

                "chat_id": chat_id,

                "chat_type":
                    chat_type or "",

                "title":
                    title or "",

                "updated_at": now
            },

            "$setOnInsert": {
                "created_at": now
            }
        },

        upsert=True
    )

    return True


async def count_chats():

    return await chats_collection.count_documents(
        {}
    )

# ============================================================
# REQUEST SYSTEM
# ============================================================

async def can_make_request(
    user_id
):

    user = await get_user(
        user_id
    )

    if not user:
        return False

    try:

        remaining = int(
            user.get(
                "remaining_requests",
                0
            ) or 0
        )

    except Exception:

        remaining = 0

    return remaining > 0


async def activate_premium(
    user_id,
    plan_name,
    amount,
    requests
):

    result = await users_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {

                "premium": True,

                "plan": plan_name,

                "paid_amount": amount,

                "premium_requests": requests,

                "remaining_requests": requests,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )

async def remove_premium(
    user_id
):

    result = await users_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$set": {

                "premium": False,

                "plan": "Free",

                "paid_amount": 0,

                "premium_requests": 0,

                "remaining_requests":
                    FREE_REQUESTS,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )

async def consume_request(
    user_id
):

    result = await users_collection.update_one(

        {
            "user_id": user_id,

            "remaining_requests": {
                "$gt": 0
            }
        },

        {
            "$inc": {

                "remaining_requests": -1,

                "total_requests_used": 1
            },

            "$set": {
                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )

async def restore_request(
    user_id
):

    result = await users_collection.update_one(

        {
            "user_id": user_id
        },

        {
            "$inc": {

                "remaining_requests": 1,

                "total_requests_used": -1
            },

            "$set": {
                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )

# ============================================================
# MEDIA
# ============================================================

async def add_media(
    data
):

    if not data:
        return False

    channel_id = data.get(
        "channel_id"
    )

    message_id = data.get(
        "message_id"
    )

    if channel_id is None:
        return False

    if message_id is None:
        return False

    await media_collection.update_one(

        {
            "channel_id": channel_id,

            "message_id": message_id
        },

        {
            "$set": data
        },

        upsert=True
    )

    return True


async def get_media(
    channel_id,
    message_id
):

    return await media_collection.find_one(

        {
            "channel_id": channel_id,

            "message_id": message_id
        }
    )


async def get_media_by_message(
    channel_id,
    message_id
):

    try:

        return await media_collection.find_one(

            {
                "channel_id": int(
                    channel_id
                ),

                "message_id": int(
                    message_id
                )
            }
        )

    except Exception as e:

        logger.error(
            "get_media_by_message error: %s",
            e
        )

        return None


async def count_media():

    return await media_collection.count_documents(
        {}
    )


# ============================================================
# MEDIA STORAGE
# ============================================================

async def get_media_storage_stats():

    pipeline = [

        {
            "$group": {

                "_id": None,

                "total_files": {
                    "$sum": 1
                },

                "total_size": {
                    "$sum": {
                        "$ifNull": [
                            "$file_size",
                            0
                        ]
                    }
                }
            }
        }
    ]

    result = await media_collection.aggregate(
        pipeline
    ).to_list(
        length=1
    )

    if not result:

        return {
            "total_files": 0,
            "total_size": 0
        }

    data = result[0]

    return {

        "total_files":
            data.get(
                "total_files",
                0
            ),

        "total_size":
            data.get(
                "total_size",
                0
            )
    }


# ============================================================
# SEARCH SESSION
# ============================================================

async def create_search_session(
    user_id,
    query,
    filters=None,
    search_time=0
):

    import secrets

    session_id = secrets.token_hex(
        8
    )

    document = {

        "session_id":
            session_id,

        "user_id":
            user_id,

        "query":
            query,

        "filters":
            filters or {},

        "search_time":
            float(search_time or 0),

        "created_at":
            datetime.utcnow()
    }

    await search_sessions_collection.insert_one(
        document
    )

    return session_id


async def get_search_session(
    session_id,
    user_id
):

    return await search_sessions_collection.find_one(

        {
            "session_id": session_id,

            "user_id": user_id
        }
    )


async def update_search_session_filters(
    session_id,
    user_id,
    filters=None
):

    filters = filters or {}

    allowed_fields = {

        "language",

        "year",

        "quality",

        "season",

        "episode"
    }

    clean_filters = {}

    for key, value in filters.items():

        if key not in allowed_fields:
            continue

        if value is None:
            continue

        if isinstance(
            value,
            str
        ):

            value = value.strip()

            if not value:
                continue

        clean_filters[key] = value

    result = await search_sessions_collection.update_one(

        {
            "session_id": session_id,

            "user_id": user_id
        },

        {
            "$set": {

                "filters":
                    clean_filters,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )


async def get_search_session_filters(
    session_id,
    user_id
):

    session = await get_search_session(
        session_id,
        user_id
    )

    if not session:
        return {}

    return session.get(
        "filters",
        {}
    ) or {}


async def delete_search_session(
    session_id
):

    await search_sessions_collection.delete_one(
        {
            "session_id": session_id
        }
    )


# ============================================================
# SEARCH NORMALIZATION
# ============================================================

def _normalize_search_text(
    text
):

    if text is None:
        return ""

    text = str(
        text
    ).lower()

    text = re.sub(
        r"[^a-z0-9\u0900-\u097f\u0b80-\u0bff\u0c00-\u0c7f\u0d00-\u0d7f\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def _build_search_condition(
    query
):

    normalized_query = _normalize_search_text(
        query
    )

    if not normalized_query:
        return None

    words = [

        word

        for word in normalized_query.split()

        if len(word) >= 2
    ]

    searchable_fields = [

        "title",

        "file_name",

        "filename",

        "name",

        "search_key",

        "title_key",

        "caption"
    ]

    if len(words) <= 1:

        word = (
            words[0]
            if words
            else normalized_query
        )

        word_regex = {

            "$regex":
                re.escape(word),

            "$options":
                "i"
        }

        return {

            "$or": [

                {
                    field:
                        word_regex
                }

                for field in searchable_fields
            ]
        }

    word_conditions = []

    for word in words:

        word_regex = {

            "$regex":
                re.escape(word),

            "$options":
                "i"
        }

        word_conditions.append(

            {
                "$or": [

                    {
                        field:
                            word_regex
                    }

                    for field in searchable_fields
                ]
            }
        )

    phrase_regex = {

        "$regex":
            re.escape(
                normalized_query
            ),

        "$options":
            "i"
    }

    phrase_condition = {

        "$or": [

            {
                field:
                    phrase_regex
            }

            for field in searchable_fields
        ]
    }

    return {

        "$or": [

            phrase_condition,

            {
                "$and":
                    word_conditions
            }
        ]
    }


def _apply_media_filters(
    search_filter,
    filters
):

    filters = filters or {}

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    language = filters.get(
        "language"
    )

    if language:

        language = str(
            language
        ).strip()

        if language:

            search_filter[
                "language"
            ] = {

                "$regex":
                    re.escape(
                        language
                    ),

                "$options":
                    "i"
            }

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    if filters.get(
        "year"
    ) is not None:

        try:

            search_filter[
                "year"
            ] = int(
                filters[
                    "year"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    quality = filters.get(
        "quality"
    )

    if quality:

        quality = str(
            quality
        ).strip()

        if quality:

            search_filter[
                "quality"
            ] = {

                "$regex":
                    re.escape(
                        quality
                    ),

                "$options":
                    "i"
            }

    # --------------------------------------------------------
    # SEASON
    # --------------------------------------------------------

    if filters.get(
        "season"
    ) is not None:

        try:

            search_filter[
                "season"
            ] = int(
                filters[
                    "season"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    # --------------------------------------------------------
    # EPISODE
    # --------------------------------------------------------

    if filters.get(
        "episode"
    ) is not None:

        try:

            search_filter[
                "episode"
            ] = int(
                filters[
                    "episode"
                ]
            )

        except (
            TypeError,
            ValueError
        ):

            pass

    return search_filter


# ============================================================
# SEARCH MEDIA
# ============================================================

async def search_media(
    query,
    skip=0,
    limit=10,
    filters=None
):

    if not query:
        return []

    query = str(
        query
    ).strip()

    if not query:
        return []

    search_condition = _build_search_condition(
        query
    )

    if not search_condition:
        return []

    search_filter = dict(
        search_condition
    )

    search_filter = _apply_media_filters(
        search_filter,
        filters or {}
    )

    try:

        skip = max(
            0,
            int(skip)
        )

    except Exception:

        skip = 0

    try:

        limit = max(
            1,
            int(limit)
        )

    except Exception:

        limit = 10

    logger.info(
        "Searching media: query=%r skip=%s limit=%s filters=%s",
        query,
        skip,
        limit,
        filters or {}
    )

    cursor = (

        media_collection

        .find(
            search_filter
        )

        .sort(
            "message_id",
            -1
        )

        .skip(
            skip
        )

        .limit(
            limit
        )
    )

    results = await cursor.to_list(
        length=limit
    )

    logger.info(
        "Search returned %s result(s) for %r",
        len(results),
        query
    )

    return results


# ============================================================
# FILTER OPTIONS
# ============================================================

async def get_filter_options(
    query,
    filters=None
):

    empty_result = {

        "languages": [],

        "years": [],

        "qualities": [],

        "seasons": [],

        "episodes": []
    }

    if not query:
        return empty_result

    query = str(
        query
    ).strip()

    if not query:
        return empty_result

    search_condition = _build_search_condition(
        query
    )

    if not search_condition:
        return empty_result

    base_filter = dict(
        search_condition
    )

    base_filter = _apply_media_filters(
        base_filter,
        filters or {}
    )

    # --------------------------------------------------------
    # LANGUAGES
    # --------------------------------------------------------

    language_pipeline = [

        {
            "$match":
                base_filter
        },

        {
            "$match": {

                "language": {

                    "$nin": [
                        None,
                        ""
                    ]
                }
            }
        },

        {
            "$group": {

                "_id":
                    "$language"
            }
        },

        {
            "$sort": {

                "_id":
                    1
            }
        }
    ]

    language_result = await media_collection.aggregate(
        language_pipeline
    ).to_list(
        length=None
    )

    languages = []

    for item in language_result:

        value = item.get(
            "_id"
        )

        if value:

            value = str(
                value
            ).strip()

            if value:

                languages.append(
                    value
                )

    # --------------------------------------------------------
    # YEARS
    # --------------------------------------------------------

    current_year = datetime.utcnow().year

    year_pipeline = [

        {
            "$match":
                base_filter
        },

        {
            "$match": {

                "year": {

                    "$gte":
                        1960,

                    "$lte":
                        current_year
                }
            }
        },

        {
            "$group": {

                "_id":
                    "$year"
            }
        },

        {
            "$sort": {

                "_id":
                    1
            }
        }
    ]

    year_result = await media_collection.aggregate(
        year_pipeline
    ).to_list(
        length=None
    )

    years = []

    for item in year_result:

        value = item.get(
            "_id"
        )

        if value is not None:

            try:

                value = int(
                    value
                )

                if (
                    1960
                    <= value
                    <= current_year
                ):

                    years.append(
                        value
                    )

            except (
                TypeError,
                ValueError
            ):

                pass

    # --------------------------------------------------------
    # QUALITY
    # --------------------------------------------------------

    quality_pipeline = [

        {
            "$match":
                base_filter
        },

        {
            "$match": {

                "quality": {

                    "$nin": [
                        None,
                        ""
                    ]
                }
            }
        },

        {
            "$group": {

                "_id":
                    "$quality"
            }
        },

        {
            "$sort": {

                "_id":
                    1
            }
        }
    ]

    quality_result = await media_collection.aggregate(
        quality_pipeline
    ).to_list(
        length=None
    )

    qualities = []

    for item in quality_result:

        value = item.get(
            "_id"
        )

        if value:

            value = str(
                value
            ).strip()

            if value:

                qualities.append(
                    value
                )

    # --------------------------------------------------------
    # SEASONS
    # --------------------------------------------------------

    season_pipeline = [

        {
            "$match":
                base_filter
        },

        {
            "$match": {

                "season": {

                    "$gte":
                        1,

                    "$lte":
                        20
                }
            }
        },

        {
            "$group": {

                "_id":
                    "$season"
            }
        },

        {
            "$sort": {

                "_id":
                    1
            }
        }
    ]

    season_result = await media_collection.aggregate(
        season_pipeline
    ).to_list(
        length=None
    )

    seasons = []

    for item in season_result:

        value = item.get(
            "_id"
        )

        if value is not None:

            try:

                value = int(
                    value
                )

                if 1 <= value <= 20:

                    seasons.append(
                        value
                    )

            except (
                TypeError,
                ValueError
            ):

                pass

    # --------------------------------------------------------
    # EPISODES
    # --------------------------------------------------------

    episode_pipeline = [

        {
            "$match":
                base_filter
        },

        {
            "$match": {

                "episode": {

                    "$gte":
                        1,

                    "$lte":
                        50
                }
            }
        },

        {
            "$group": {

                "_id":
                    "$episode"
            }
        },

        {
            "$sort": {

                "_id":
                    1
            }
        }
    ]

    episode_result = await media_collection.aggregate(
        episode_pipeline
    ).to_list(
        length=None
    )

    episodes = []

    for item in episode_result:

        value = item.get(
            "_id"
        )

        if value is not None:

            try:

                value = int(
                    value
                )

                if 1 <= value <= 50:

                    episodes.append(
                        value
                    )

            except (
                TypeError,
                ValueError
            ):

                pass

    return {

        "languages":
            languages,

        "years":
            years,

        "qualities":
            qualities,

        "seasons":
            seasons,

        "episodes":
            episodes
    }


# ============================================================
# STATISTICS
# ============================================================

async def count_users():

    return await users_collection.count_documents(
        {}
    )


async def count_premium_users():

    return await users_collection.count_documents(
        {
            "premium": True
        }
    )


async def get_total_file_size():

    pipeline = [

        {
            "$match": {

                "file_size": {

                    "$exists":
                        True,

                    "$type":
                        "number"
                }
            }
        },

        {
            "$group": {

                "_id":
                    None,

                "total_size": {

                    "$sum":
                        "$file_size"
                }
            }
        }
    ]

    result = await media_collection.aggregate(
        pipeline
    ).to_list(
        length=1
    )

    if not result:
        return 0

    return result[0].get(
        "total_size",
        0
    )


async def get_stats():

    users = await count_users()

    chats = await count_chats()

    premium_users = (
        await count_premium_users()
    )

    media = await count_media()

    total_size_bytes = (
        await get_total_file_size()
    )

    used_storage_mb = (
        total_size_bytes
        / (1024 * 1024)
    )

    free_storage_mb = max(
        STORAGE_LIMIT_MB
        - used_storage_mb,
        0
    )

    return {

        "users":
            users,

        "chats":
            chats,

        "premium_users":
            premium_users,

        "media":
            media,

        "total_size":
            total_size_bytes,

        "used_storage":
            used_storage_mb,

        "free_storage":
            free_storage_mb,

        "used_storage_text":
            f"{used_storage_mb:.2f} MB",

        "free_storage_text":
            f"{free_storage_mb:.2f} MB"
    }

async def get_all_user_ids():

    cursor = users_collection.find(
        {},
        {
            "_id": 0,
            "user_id": 1
        }
    )

    users = await cursor.to_list(length=None)

    return [
        user["user_id"]
        for user in users
        if user.get("user_id") is not None
    ]

# ============================================================
# INDEXER STATE
# ============================================================

async def get_indexer_state():

    state = await settings_collection.find_one(
        {
            "_id": "indexer"
        }
    )

    if not state:

        return {

            "last_message_id":
                0,

            "indexed_count":
                0,

            "updated_at":
                None
        }

    return state


async def save_indexer_state(
    last_message_id,
    indexed_count
):

    await settings_collection.update_one(

        {
            "_id":
                "indexer"
        },

        {
            "$set": {

                "last_message_id":
                    last_message_id,

                "indexed_count":
                    indexed_count,

                "updated_at":
                    datetime.utcnow()
            }
        },

        upsert=True
    )


async def update_indexer_state(
    last_message_id=None,
    indexed_count=None
):

    update = {

        "updated_at":
            datetime.utcnow()
    }

    if last_message_id is not None:

        update[
            "last_message_id"
        ] = last_message_id

    if indexed_count is not None:

        update[
            "indexed_count"
        ] = indexed_count

    await settings_collection.update_one(

        {
            "_id":
                "indexer"
        },

        {
            "$set":
                update
        },

        upsert=True
    )

    return True


async def reset_indexer():

    await settings_collection.update_one(

        {
            "_id":
                "indexer"
        },

        {
            "$set": {

                "last_message_id":
                    0,

                "indexed_count":
                    0,

                "updated_at":
                    datetime.utcnow()
            }
        },

        upsert=True
    )


# ============================================================
# FORCE SUB
# ============================================================

async def get_fsub_channels():

    document = await settings_collection.find_one(
        {
            "_id": "fsub"
        }
    )

    if not document:
        return []

    return document.get(
        "channels",
        []
    )


async def add_fsub_channel(
    channel_data
):

    if not channel_data:
        return False

    chat_id = channel_data.get(
        "chat_id"
    )

    if chat_id is None:
        return False

    existing = await settings_collection.find_one(

        {
            "_id":
                "fsub",

            "channels.chat_id":
                chat_id
        }
    )

    if existing:
        return False

    await settings_collection.update_one(

        {
            "_id":
                "fsub"
        },

        {
            "$push": {

                "channels":
                    channel_data
            }
        },

        upsert=True
    )

    return True


async def remove_fsub_channel(
    chat_id
):

    result = await settings_collection.update_one(

        {
            "_id":
                "fsub"
        },

        {
            "$pull": {

                "channels": {

                    "chat_id":
                        chat_id
                }
            }
        }
    )

    return (
        result.modified_count > 0
    )


# ============================================================
# TRENDING
# ============================================================

async def record_search(
    query
):

    if not query:
        return False

    query = str(
        query
    ).strip()

    if not query:
        return False

    if query.startswith("/"):
        return False

    await settings_collection.update_one(

        {
            "_id":
                "search_trends"
        },

        {
            "$inc": {

                f"queries.{query}":
                    1
            },

            "$set": {

                "updated_at":
                    datetime.utcnow()
            }
        },

        upsert=True
    )

    return True


async def get_trending_searches(
    limit=29
):

    document = await settings_collection.find_one(

        {
            "_id":
                "search_trends"
        }
    )

    if not document:
        return []

    queries = document.get(
        "queries",
        {}
    )

    if not queries:
        return []

    valid_queries = {}

    for query, count in queries.items():

        query = str(
            query
        ).strip()

        if not query:
            continue

        if query.startswith("/"):
            continue

        if isinstance(
            count,
            (int, float)
        ):

            valid_queries[
                query
            ] = int(
                count
            )

    sorted_queries = sorted(

        valid_queries.items(),

        key=lambda item:
            item[1],

        reverse=True
    )

    return sorted_queries[
        :int(limit)
    ]


# ============================================================
# REDEEM CODES
# ============================================================

async def create_redeem_code(
    code,
    amount,
    created_by
):

    if not code:
        return False

    try:

        amount = int(
            amount
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    if amount <= 0:
        return False

    document = {

        "code":
            str(code).upper().strip(),

        "amount":
            amount,

        "used":
            False,

        "used_by":
            None,

        "used_at":
            None,

        "created_by":
            created_by,

        "created_at":
            datetime.utcnow()
    }

    try:

        await redeem_codes_collection.insert_one(
            document
        )

        return True

    except Exception as e:

        logger.warning(
            "Could not create redeem code: %s",
            e
        )

        return False


async def get_redeem_codes():

    cursor = redeem_codes_collection.find(
        {}
    ).sort(
        "created_at",
        -1
    )

    return await cursor.to_list(
        length=None
    )


async def get_redeem_code(
    code
):

    if not code:
        return None

    return await redeem_codes_collection.find_one(

        {
            "code":
                str(code).upper().strip()
        }
    )


async def redeem_code(
    code,
    user_id
):

    if not code:

        return {
            "success":
                False,

            "reason":
                "invalid_code"
        }

    code = str(
        code
    ).upper().strip()

    result = await redeem_codes_collection.find_one_and_update(

        {
            "code":
                code,

            "used":
                False
        },

        {
            "$set": {

                "used":
                    True,

                "used_by":
                    user_id,

                "used_at":
                    datetime.utcnow()
            }
        },

        return_document=
            ReturnDocument.AFTER
    )

    if not result:

        existing = await get_redeem_code(
            code
        )

        if not existing:

            return {
                "success":
                    False,

                "reason":
                    "code_not_found"
            }

        if existing.get(
            "used"
        ):

            return {
                "success":
                    False,

                "reason":
                    "already_used"
            }

        return {
            "success":
                False,

            "reason":
                "redeem_failed"
        }

    return {

        "success":
            True,

        "reason":
            "redeemed",

        "amount":
            int(
                result.get(
                    "amount",
                    0
                ) or 0
            )
    }


async def delete_redeem_code(
    code
):

    if not code:
        return False

    result = await redeem_codes_collection.delete_one(

        {
            "code":
                str(code).upper().strip()
        }
    )

    return (
        result.deleted_count > 0
    )


async def count_redeem_codes():

    return await redeem_codes_collection.count_documents(
        {}
    )


async def count_unused_redeem_codes():

    return await redeem_codes_collection.count_documents(

        {
            "used":
                False
        }
    )


# ============================================================
# BAN SYSTEM
# ============================================================

async def ban_user(
    user_id,
    banned_by=None,
    reason=""
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    now = datetime.utcnow()

    result = await banned_users_collection.update_one(

        {
            "user_id":
                user_id
        },

        {
            "$set": {

                "user_id":
                    user_id,

                "banned":
                    True,

                "reason":
                    reason or "",

                "banned_by":
                    banned_by,

                "banned_at":
                    now
            }
        },

        upsert=True
    )

    return (
        result.modified_count > 0
        or result.upserted_id is not None
    )


async def unban_user(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    result = await banned_users_collection.delete_one(

        {
            "user_id":
                user_id
        }
    )

    return (
        result.deleted_count > 0
    )


async def is_user_banned(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    user = await banned_users_collection.find_one(

        {
            "user_id":
                user_id
        }
    )

    return user is not None


async def get_banned_user(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    return await banned_users_collection.find_one(

        {
            "user_id":
                user_id
        }
    )


async def get_banned_users():

    cursor = banned_users_collection.find(
        {}
    ).sort(
        "banned_at",
        -1
    )

    return await cursor.to_list(
        length=None
    )


async def count_banned_users():

    return await banned_users_collection.count_documents(
        {}
    )


# ============================================================
# MAINTENANCE
# ============================================================

async def set_maintenance(
    enabled
):

    enabled = bool(
        enabled
    )

    await settings_collection.update_one(

        {
            "_id":
                "maintenance"
        },

        {
            "$set": {

                "enabled":
                    enabled,

                "updated_at":
                    datetime.utcnow()
            }
        },

        upsert=True
    )

    return enabled


async def is_maintenance_enabled():

    document = await settings_collection.find_one(

        {
            "_id":
                "maintenance"
        }
    )

    if not document:
        return False

    return bool(
        document.get(
            "enabled",
            False
        )
    )


async def get_maintenance_status():

    document = await settings_collection.find_one(

        {
            "_id":
                "maintenance"
        }
    )

    if not document:

        return {

            "enabled":
                False,

            "updated_at":
                None
        }

    return {

        "enabled":
            bool(
                document.get(
                    "enabled",
                    False
                )
            ),

        "updated_at":
            document.get(
                "updated_at"
            )
    }


# ============================================================
# ADMIN MANAGEMENT
# ============================================================

async def add_admin(
    user_id,
    added_by=None,
    first_name="",
    username=""
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    now = datetime.utcnow()

    document = {

        "user_id":
            user_id,

        "first_name":
            first_name or "",

        "username":
            username or "",

        "added_by":
            added_by,

        "added_at":
            now,

        "updated_at":
            now
    }

    try:

        await admins_collection.insert_one(
            document
        )

        return True

    except Exception as e:

        logger.warning(
            "Could not add admin %s: %s",
            user_id,
            e
        )

        return False


async def remove_admin(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    result = await admins_collection.delete_one(

        {
            "user_id":
                user_id
        }
    )

    return (
        result.deleted_count > 0
    )


async def is_admin(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    admin = await admins_collection.find_one(

        {
            "user_id":
                user_id
        }
    )

    return admin is not None


async def get_admin(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    return await admins_collection.find_one(

        {
            "user_id":
                user_id
        }
    )


async def get_admins():

    cursor = admins_collection.find(
        {}
    ).sort(
        "added_at",
        1
    )

    return await cursor.to_list(
        length=None
    )


async def count_admins():

    return await admins_collection.count_documents(
        {}
    )


async def update_admin_info(
    user_id,
    first_name=None,
    username=None
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    update = {

        "updated_at":
            datetime.utcnow()
    }

    if first_name is not None:

        update[
            "first_name"
        ] = first_name or ""

    if username is not None:

        update[
            "username"
        ] = username or ""

    result = await admins_collection.update_one(

        {
            "user_id":
                user_id
        },

        {
            "$set":
                update
        }
    )

    return (
        result.matched_count > 0
    )


# ============================================================
# ADMIN WARN SYSTEM
# ============================================================

async def add_warning(
    user_id,
    warned_by=None,
    reason=""
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return None

    now = datetime.utcnow()

    result = await users_collection.find_one_and_update(

        {
            "user_id":
                user_id
        },

        {
            "$inc": {
                "warnings": 1
            },

            "$set": {
                "last_warning_reason":
                    reason or "",

                "last_warned_by":
                    warned_by,

                "last_warned_at":
                    now,

                "updated_at":
                    now
            }
        },

        return_document=ReturnDocument.AFTER
    )

    if not result:

        return None

    return int(
        result.get(
            "warnings",
            0
        ) or 0
    )


async def get_warnings(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return 0

    user = await users_collection.find_one(

        {
            "user_id":
                user_id
        },

        {
            "_id": 0,
            "warnings": 1
        }
    )

    if not user:

        return 0

    return int(
        user.get(
            "warnings",
            0
        ) or 0
    )


async def reset_warnings(
    user_id
):

    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    result = await users_collection.update_one(

        {
            "user_id":
                user_id
        },

        {
            "$set": {

                "warnings":
                    0,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return (
        result.matched_count > 0
    )

async def get_all_warnings():
    cursor = users_collection.find(
        {"warnings": {"$gt": 0}},
        {
            "_id": 0,
            "user_id": 1,
            "first_name": 1,
            "username": 1,
            "warnings": 1,
            "last_warning_reason": 1,
            "last_warned_by": 1,
            "last_warned_at": 1
        }
    ).sort(
        "warnings",
        -1
    )

    return await cursor.to_list(length=None)


async def remove_warning(user_id):
    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return False

    result = await users_collection.update_one(
        {
            "user_id": user_id,
            "warnings": {"$gt": 0}
        },
        {
            "$inc": {
                "warnings": -1
            },
            "$set": {
                "updated_at": datetime.utcnow()
            }
        }
    )

    return result.modified_count > 0
    
# ============================================================
# ADMIN CONFIGURATION
# ============================================================

async def get_admin_settings():

    document = await settings_collection.find_one(

        {
            "_id":
                "admin_settings"
        }
    )

    if not document:

        return {}

    return document


async def save_admin_settings(
    data
):

    if not data:

        return False

    await settings_collection.update_one(

        {
            "_id":
                "admin_settings"
        },

        {
            "$set": data
        },

        upsert=True
    )

    return True

# ============================================================
# DATABASE OPTIMIZATION
# ============================================================

async def optimize_database():
    """
    Safely optimize MongoDB.

    IMPORTANT:
    - Never deletes media/movie records.
    - Cleans only expired search sessions when expires_at exists.
    - Ensures important indexes exist.
    - Reports database statistics.
    """

    global db
    global users_collection
    global media_collection
    global search_sessions_collection
    global settings_collection
    global chats_collection

    if db is None:
        raise RuntimeError(
            "Database is not initialized."
        )

    result = {
        "collections_checked": 0,
        "sessions_cleaned": 0,
        "indexes_checked": 0,
        "users": 0,
        "chats": 0,
        "files": 0,
        "storage_mb": 0,
    }

    # --------------------------------------------------------
    # COLLECTIONS
    # --------------------------------------------------------

    collections = [
        "users",
        "media",
        "search_sessions",
        "settings",
        "chats",
    ]

    existing_collections = (
        await db.list_collection_names()
    )

    for collection_name in collections:

        if collection_name in existing_collections:

            result[
                "collections_checked"
            ] += 1

    # --------------------------------------------------------
    # CLEAN EXPIRED SEARCH SESSIONS
    # --------------------------------------------------------

    if search_sessions_collection is not None:

        try:

            cleanup_result = (
                await search_sessions_collection.delete_many(
                    {
                        "expires_at": {
                            "$exists": True,
                            "$lte": datetime.utcnow()
                        }
                    }
                )
            )

            result[
                "sessions_cleaned"
            ] = cleanup_result.deleted_count

        except Exception as e:

            logger.warning(
                "Search session cleanup failed: %s",
                e
            )

            result[
                "sessions_cleaned"
            ] = 0

    # --------------------------------------------------------
    # REQUIRED INDEXES
    # --------------------------------------------------------

    required_indexes = [

        (
            users_collection,
            "user_id",
            [("user_id", 1)],
            {"unique": True}
        ),

        (
            chats_collection,
            "chat_id",
            [("chat_id", 1)],
            {"unique": True}
        ),

        (
            search_sessions_collection,
            "session_id",
            [("session_id", 1)],
            {"unique": True}
        ),

        (
            search_sessions_collection,
            "user_id",
            [("user_id", 1)],
            {}
        ),

        (
            media_collection,
            "message_id",
            [("message_id", 1)],
            {}
        ),

        (
            media_collection,
            "title_key",
            [("title_key", 1)],
            {}
        ),

        (
            media_collection,
            "search_key",
            [("search_key", 1)],
            {}
        ),

        (
            media_collection,
            "channel_id_message_id",
            [
                ("channel_id", 1),
                ("message_id", 1)
            ],
            {"unique": True}
        ),
    ]

    # --------------------------------------------------------
    # CREATE / CHECK INDEXES
    # --------------------------------------------------------

    for (
        collection,
        index_name,
        keys,
        options
    ) in required_indexes:

        if collection is None:
            continue

        index_result = await ensure_index(
            collection,
            keys,
            name=index_name,
            unique=options.get(
                "unique",
                False
            )
        )

        if index_result is not None:

            result[
                "indexes_checked"
            ] += 1

    # --------------------------------------------------------
    # USER STATISTICS
    # --------------------------------------------------------

    try:

        if users_collection is not None:

            result[
                "users"
            ] = await users_collection.count_documents(
                {}
            )

    except Exception as e:

        logger.warning(
            "User count failed: %s",
            e
        )

        result[
            "users"
        ] = 0

    # --------------------------------------------------------
    # CHAT STATISTICS
    # --------------------------------------------------------

    try:

        if chats_collection is not None:

            result[
                "chats"
            ] = await chats_collection.count_documents(
                {}
            )

    except Exception as e:

        logger.warning(
            "Chat count failed: %s",
            e
        )

        result[
            "chats"
        ] = 0

    # --------------------------------------------------------
    # MEDIA / FILE STATISTICS
    # --------------------------------------------------------

    try:

        if media_collection is not None:

            result[
                "files"
            ] = await media_collection.count_documents(
                {}
            )

    except Exception as e:

        logger.warning(
            "Media count failed: %s",
            e
        )

        result[
            "files"
        ] = 0

    # --------------------------------------------------------
    # STORAGE STATISTICS
    # --------------------------------------------------------

    try:

        storage = (
            await get_media_storage_stats()
        )

        if isinstance(
            storage,
            dict
        ):

            total_size = storage.get(
                "total_size",
                0
            ) or 0

            result[
                "storage_mb"
            ] = round(
                float(total_size)
                / (1024 * 1024),
                2
            )

    except Exception as e:

        logger.warning(
            "Storage calculation failed: %s",
            e
        )

        result[
            "storage_mb"
        ] = 0

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #

    logger.info(
        "Database optimization completed: %s",
        result
    )

    return result

# ------------------------ #
# Don't Remove My Credits
# Owner: @Mr_Mohammed_29
# Updates: @Aero_Unity 
# Support : @Coders_Grp 
# ------------------------ #
