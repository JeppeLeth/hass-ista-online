import asyncio
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryAuthFailed
from typing import Any, Dict
from datetime import timedelta

from . import const
from .api_client import fetch_token, fetch_user_info, fetch_meters, TokenSuccess

import logging

_LOGGER = logging.getLogger(__name__)


class ISTACoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, base_url: str, username: str, password: str):
        super().__init__(
            hass,
            _LOGGER,
            name="ISTA Online",
            update_interval=timedelta(seconds=const.UPDATE_INTERVAL_SECONDS),
        )
        self.base_url = base_url
        self.username = username
        self.password = password
        self.user_info: Dict[str, Any] = {}
        self.meters: Dict[str, Any] = {}

    async def _async_update_data(self) -> Dict[str, Any]:
        def sync_fetch():
            token_result = fetch_token(self.base_url, self.username, self.password)
            if not isinstance(token_result, TokenSuccess):
                err = getattr(token_result, "error", "")
                descr = getattr(token_result, "error_description", None) or ""
                if err == "invalid_grant":
                    raise ConfigEntryAuthFailed(f"Authentication failed: {descr}")
                raise UpdateFailed(f"Token error: {descr or err}")
            bearer = token_result.auth_header()

            user_info, err = fetch_user_info(self.base_url, bearer)
            if err:
                raise UpdateFailed(f"UserInfo error: {err}")

            meters_data, err = fetch_meters(self.base_url, bearer)
            if err:
                raise UpdateFailed(f"Meters error: {err}")

            return {
                "token": token_result,
                "user_info": user_info or {},
                "meters": meters_data or {},
            }

        try:
            result = await self.hass.async_add_executor_job(sync_fetch)
        except ConfigEntryAuthFailed:
            raise
        except UpdateFailed:
            raise
        except Exception as e:
            raise UpdateFailed(f"Unexpected error fetching ISTA data: {e}")

        self.user_info = result["user_info"]
        self.meters = result["meters"]
        return result
