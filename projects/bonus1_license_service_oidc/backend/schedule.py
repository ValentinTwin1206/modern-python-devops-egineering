"""Background scheduling for Cloudsmith user-token refreshes."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from license_service.cloudsmith import (
    CloudsmithClient,
    CloudsmithConfig,
    CloudsmithConfigurationError,
)

if TYPE_CHECKING:
    from license_service.database import Database

logger = logging.getLogger("license-service.scheduler")
TOKEN_DURATION_SECONDS = 3600


def _get_refreshed_token(response: dict) -> str:
    token = response.get("token") or response.get("key") or response.get("api_key")
    if not isinstance(token, str) or not token:
        raise CloudsmithConfigurationError(
            "Cloudsmith returned a response without a user token"
        )
    return token


def refresh_and_store_cloudsmith_token(
    config: CloudsmithConfig,
    database: Database,
) -> dict[str, str]:
    """Refresh the Cloudsmith token and store it as a one-hour license."""
    get_latest_active_license = getattr(database, "get_latest_active_license", None)
    existing = get_latest_active_license() if get_latest_active_license else None
    logger.info(
        "Starting Cloudsmith token refresh: existing_token=%s existing_expires_at=%s",
        existing is not None,
        existing["expires_at"] if existing is not None else None,
    )

    response = CloudsmithClient(config).refresh_user_token()
    logger.info(
        "Cloudsmith token refresh response received: fields=%s",
        sorted(response.keys()),
    )
    token = _get_refreshed_token(response)
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=TOKEN_DURATION_SECONDS
    )
    result = {
        "user": "cloudsmith-user-token",
        "cloudsmith_token": token,
        "cloudsmith_expires_at": expires_at.isoformat(),
    }
    database.save_license(
        token,
        result["cloudsmith_expires_at"],
        result["user"],
        "",
        None,
        config.token_slug_perm,
    )
    logger.info(
        "Cloudsmith token stored: token_present=%s expires_at=%s",
        bool(token),
        result["cloudsmith_expires_at"],
    )
    return result


async def cloudsmith_refresh_loop(
    config: CloudsmithConfig,
    database: Database,
    interval_seconds: int = TOKEN_DURATION_SECONDS,
) -> None:
    """Refresh the Cloudsmith token repeatedly until the task is cancelled."""
    logger.info(
        "Cloudsmith refresh scheduler started: interval_seconds=%s",
        interval_seconds,
    )
    while True:
        try:
            await asyncio.to_thread(
                refresh_and_store_cloudsmith_token,
                config,
                database,
            )
            logger.info("Cloudsmith user token refreshed by scheduler")
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Scheduled Cloudsmith token refresh failed")
        logger.info(
            "Next Cloudsmith token refresh scheduled in %s seconds",
            interval_seconds,
        )
        await asyncio.sleep(interval_seconds)
