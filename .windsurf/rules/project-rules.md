---
trigger: always_on
---

# Python Style Guide - Complete Documentation

## Part 01 — Imports Layout

Group Imports With Explicit Headers In This Order:

* **Standard Library Imports**
* **Third Party Imports**
* **Local Imports**

One Blank Line Between Groups.
No Unused Imports.

**Example:**

```python
# Standard Library Imports
import datetime
from typing import Any

# Third Party Imports
import jwt
from fastapi import status
from fastapi.responses import JSONResponse
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.database import AsyncDatabase
from redis.asyncio import Redis as AsyncRedis

# Local Imports
from config.mongodb import get_async_mongodb
from config.redis_cache import get_async_redis
from config.settings import settings
from src.models.users import User
```

## Part 02 — Commenting Conventions

* All Comments Are **Single-Line** And **Title Case**.
* **One Comment Per Line Of Code** - No Grouping Comments For Multiple Lines.
* **Comments Required Above All Function Definitions**.
* Place Comments Immediately **Above** The Single Line They Describe.
* Comments Must Be **Short (4-5 Words Max)** And Informative.
* **No Inline Comments** Except For Linting/Testing Ignores (e.g., `# noqa: E501`, `# type: ignore`).
* **No Multi-Line Comments** In Any Situation.
* **No Comments Above `try`** Statements.
* **No Comments Above `except`** Statements.
* **No Comments Above Context Manager Suppressions** (e.g., `contextlib.suppress`).
* If A Single Statement Spans Multiple Lines, Only **One Comment Above The Entire Block**.

**Correct Examples:**

```python
# Get Current Time
current_time: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

# Calculate Expiry Time  
expiry_time: datetime.datetime = current_time + datetime.timedelta(seconds=settings.ACCESS_JWT_EXPIRE)

# Generate Access Token
access_token: str = jwt.encode(
    payload={
        "sub": str(user.id),
        "iss": settings.PROJECT_NAME,
        "aud": settings.PROJECT_NAME,
        "iat": current_time,
        "exp": expiry_time,
    },
    key=settings.ACCESS_JWT_SECRET,
    algorithm=settings.ACCESS_JWT_ALGORITHM,
)
```

**Incorrect Examples:**

```python
# DON'T DO THIS - No comment above try
try:
    # Decode Access Token
    jwt.decode(jwt=access_token, key=settings.ACCESS_JWT_SECRET)

    # Set Flag False
    is_valid = False

# DON'T DO THIS - No comment above except  
except jwt.InvalidTokenError:
    # Set Flag True
    is_valid = True

# DON'T DO THIS - No comment above suppress
with contextlib.suppress(KeyError):
    # Delete Cache Key
    del cache[key]

# DON'T DO THIS - Multiple lines grouped under one comment
# Process user data and validate credentials
username = request.username.strip()
password = request.password
is_valid = validate_user(username, password)
```

**Correct Exception Handling:**

```python
try:
    # Decode Access Token
    jwt.decode(jwt=access_token, key=settings.ACCESS_JWT_SECRET)

    # Set Valid Flag
    is_valid = True

except jwt.InvalidTokenError:
    # Set Invalid Flag
    is_valid = False
```

**Correct Context Manager Suppression:**

```python
# Supress KeyError
with contextlib.suppress(KeyError):
    # Delete Cache Entry
    del cache[key]
```

## Part 03 — Type Hints For Everything

Add Explicit Type Hints For:

* Function Parameters And Return Values
* All Local Variables That Hold Important State Or External Resources
* Annotate External Adapters Right After Acquisition With A **"Type Hint"** Comment
* Prefer Precise Types (`dict[str, dict[str, Any]]`) Over `Any`.

**Example:**

```python
# Generate Access Token Function
async def _generate_access_token(user: User) -> str:
    """
    Generate Access Token.

    Args:
        user (User): User Instance.

    Returns:
        str: Access Token.

    Raises:
        Exception: For Any Unexpected Errors During Access Token Generation.
    """

    # Get Current Time
    current_time: datetime.datetime = datetime.datetime.now(tz=datetime.UTC)

    # Calculate Expiry Time
    expiry_time: datetime.datetime = current_time + datetime.timedelta(seconds=settings.ACCESS_JWT_EXPIRE)

    # Generate Access Token
    access_token: str = jwt.encode(
        payload={
            "sub": str(user.id),
            "iss": settings.PROJECT_NAME,
            "aud": settings.PROJECT_NAME,
            "iat": current_time,
            "exp": expiry_time,
        },
        key=settings.ACCESS_JWT_SECRET,
        algorithm=settings.ACCESS_JWT_ALGORITHM,
    )

    # Get Redis Adapter
    async with get_async_redis(db=settings.REDIS_TOKEN_CACHE_DB) as redis:
        # Type Hint
        redis: AsyncRedis

        # Set Access Token
        await redis.set(
            f"access_token:{user.id}",
            value=access_token,
            ex=settings.ACCESS_JWT_EXPIRE,
        )

    # Return Access Token
    return access_token
```

## Part 04 — Docstrings Style And Location

* Use A **Triple-Quoted Docstring** Immediately Under Every Function Definition.
* **Title Line First**.
* Sections In This Order: **Args**, **Returns**, **Raises**.
* Parameter And Return Descriptions Use **Title Case** Phrases.
* Keep Blank Lines Between Sections.

**Example:**

```python
# Check Token Requirements Function
async def _check_if_new_tokens_required(user: User) -> dict[str, dict[str, Any]]:
    """
    Check If New Access & Refresh Token Are Required.

    Args:
        user (User): User Instance.

    Returns:
        dict[str, dict[str, Any]]: Dictionary Containing Cached Tokens And Flags
            Indicating Whether Regeneration Is Required.

    Raises:
        Exception: For Any Unexpected Errors During Token Check Flow.
    """
```

## Part 05 — Control Flow And Error Handling

* Use `try/except` Blocks Around Token Decode To Set Boolean Flags.
* Catch **Library-Specific Exceptions** (e.g., `jwt.InvalidTokenError`).
* Use **Explicit Flag Variables** With Default Values, Update Based On Outcomes.
* **No Comments Above `try` Or `except` Statements**.

**Example:**

```python
# Check Access Token
if access_token:
    try:
        # Decode Access Token
        jwt.decode(
            jwt=access_token,
            key=settings.ACCESS_JWT_SECRET,
            algorithms=[settings.ACCESS_JWT_ALGORITHM],
            verify=True,
            audience=settings.PROJECT_NAME,
            issuer=settings.PROJECT_NAME,
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_iss": True,
                "verify_exp": True,
                "strict_aud": True,
            },
        )

        # Set Valid Flag
        is_new_access_token_required = False

    except jwt.InvalidTokenError:
        # Set Invalid Flag
        is_new_access_token_required = True
```

## Part 06 — String Case And Values

* Use **Title Case** For:
  * Comments
  * Docstring Titles And Section Headers
  * Response Descriptions And Example Summaries
  * `"detail"` Messages In Example Values
* Preserve Exact Snake/Param Names For:
  * `status_code`
  * `response_model`
  * `responses`
  * JSON Keys

## Part 07 — Spacing, Newlines, And Formatting

* One Blank Line Between:
  * Import Groups
  * Top-Level Functions
  * Logical Blocks Within Functions
* Multiline Dicts And Calls:
  * Trailing Commas
  * One Item Per Line For Readability
* Keep In-Function Sections Separated By **One Blank Line** And A **Single-Line Title Case** Comment.

## Part 08 — Exports

* Add Explicit `__all__` At End Of File.
* Annotate Its Type.

**Example:**

```python
# Exports
__all__: list[str] = ["login_user"]
```
