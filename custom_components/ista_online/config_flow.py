from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN, COUNTRY_OPTIONS, DEFAULT_COUNTRY
from typing import Any, Dict
from .api_client import fetch_token, TokenSuccess
from homeassistant.config_entries import ConfigEntry

class ISTAConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self._data: Dict[str, Any] = {}

    async def async_step_user(self, user_input: Dict[str, Any] = None):
        errors: Dict[str, str] = {}
        if user_input is not None:
            country = user_input.get("country")
            username = user_input.get("username")
            password = user_input.get("password")
            if not country or not username or not password:
                errors["base"] = "missing_fields"
            else:
                base_url = COUNTRY_OPTIONS.get(country)
                if not base_url:
                    errors["country"] = "invalid_country"
                else:
                    token_res = await self.hass.async_add_executor_job(fetch_token, base_url, username, password)
                    if not isinstance(token_res, TokenSuccess):
                        errors["base"] = "auth_failed"
                    else:
                        title = f"ISTA user {username}"
                        return self.async_create_entry(
                            title=title,
                            data={"country": country, "username": username, "password": password},
                        )

        schema = vol.Schema(
            {
                vol.Required("country", default=self._data.get("country", DEFAULT_COUNTRY)): vol.In(list(COUNTRY_OPTIONS.keys())),
                vol.Required("username", default=self._data.get("username", "")): str,
                vol.Required("password"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reauth(self, user_input: Dict[str, Any] = None):
        entry: ConfigEntry = self.context.get("entry")
        if not entry:
            return self.async_abort(reason="no_entry")

        errors: Dict[str, str] = {}
        stored = dict(entry.data)
        if user_input is not None:
            username = user_input.get("username")
            password = user_input.get("password")
            country = stored.get("country", DEFAULT_COUNTRY)
            if not country or not username or not password:
                errors["base"] = "missing_fields"
            else:
                base_url = COUNTRY_OPTIONS.get(country)
                if not base_url:
                    errors["country"] = "invalid_country"
                else:
                    token_res = await self.hass.async_add_executor_job(fetch_token, base_url, username, password)
                    if not isinstance(token_res, TokenSuccess):
                        errors["base"] = "auth_failed"
                    else:
                        new_data = {"country": country, "username": username, "password": password}
                        self.hass.config_entries.async_update_entry(entry, data=new_data)
                        return self.async_abort(reason="reauth_successful")

        schema = vol.Schema(
            {
                vol.Required("username", default=stored.get("username", "")): str,
                vol.Required("password"): str,
            }
        )
        return self.async_show_form(step_id="reauth", data_schema=schema, errors=errors)

    def async_get_options_flow(self):
        return OptionsFlowHandler(self)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_flow: ISTAConfigFlow):
        self.config_flow = config_flow

    async def async_step_init(self, user_input: Dict[str, Any] = None):
        errors: Dict[str, str] = {}
        current = self.config_entry.data if self.config_entry else {}
        if user_input is not None:
            country = user_input.get("country")
            username = user_input.get("username")
            password = user_input.get("password")
            if not country or not username or not password:
                errors["base"] = "missing_fields"
            else:
                base_url = COUNTRY_OPTIONS.get(country)
                if not base_url:
                    errors["country"] = "invalid_country"
                else:
                    token_res = await self.hass.async_add_executor_job(fetch_token, base_url, username, password)
                    if not isinstance(token_res, TokenSuccess):
                        errors["base"] = "auth_failed"
                    else:
                        new_data = {"country": country, "username": username, "password": password}
                        self.hass.config_entries.async_update_entry(self.config_entry, data=new_data)
                        return self.async_create_entry(title="", data={})

        schema = vol.Schema(
            {
                vol.Required("country", default=current.get("country", DEFAULT_COUNTRY)): vol.In(list(COUNTRY_OPTIONS.keys())),
                vol.Required("username", default=current.get("username", "")): str,
                vol.Required("password"): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
