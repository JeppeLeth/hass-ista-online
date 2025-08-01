import requests
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple, Union


def _parse_utc_z(dt_str: Optional[str]) -> Optional[datetime]:
    if not dt_str or not isinstance(dt_str, str):
        return None
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


class TokenResult:
    def __init__(self, raw: Any):
        self.raw = raw


class TokenSuccess(TokenResult):
    def __init__(self, data: Dict[str, Any]):
        super().__init__(data)
        self.access_token: str = data.get("access_token") or ""
        self.token_type: str = (data.get("token_type") or "bearer").lower()
        self.expires_in: Optional[int] = None
        if isinstance(data.get("expires_in"), int):
            self.expires_in = data.get("expires_in")
        elif isinstance(data.get("expires_in"), str):
            try:
                self.expires_in = int(data.get("expires_in"))
            except Exception:
                self.expires_in = None
        self.issued_at = _parse_utc_z(data.get(".issued"))
        self.expires_at = _parse_utc_z(data.get(".expires"))
        self.first_name = data.get("FirstName")
        self.username = data.get("Username")
        self.language = data.get("Language")
        self.is_admin = None
        if "isAdmin" in data and data.get("isAdmin") is not None:
            self.is_admin = str(data.get("isAdmin")).lower() == "true"
        self.is_tenant = None
        if "isTenant" in data and data.get("isTenant") is not None:
            self.is_tenant = str(data.get("isTenant")).lower() == "true"
        self.portal_admin_id = data.get("PortalAdminId")
        self.instance_id = data.get("InstanceId")
        consumed = {
            "access_token",
            "token_type",
            "expires_in",
            ".issued",
            ".expires",
            "FirstName",
            "Username",
            "Language",
            "isAdmin",
            "isTenant",
            "PortalAdminId",
            "InstanceId",
        }
        self.extra = {k: v for k, v in data.items() if k not in consumed}

    def auth_header(self) -> str:
        return f"{self.token_type} {self.access_token}"


class TokenError(TokenResult):
    def __init__(self, error: Optional[str], error_description: Optional[str], http_status: Optional[int], raw: Any):
        super().__init__(raw)
        self.error = error
        self.error_description = error_description
        self.http_status = http_status


def fetch_token(url: str, username: str, password: str, timeout: float = 10.0) -> Union[TokenSuccess, TokenError]:
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    try:
        resp = requests.post(f"{url.rstrip('/')}/token", headers=headers, data=payload, timeout=timeout)
    except requests.RequestException as e:
        return TokenError("request_exception", str(e), None, {"exception": str(e)})

    try:
        data = resp.json()
    except ValueError:
        return TokenError("invalid_json", "Response not JSON", getattr(resp, "status_code", None), resp.text)

    if not isinstance(data, dict):
        return TokenError("bad_payload", "Unexpected token response shape", resp.status_code, data)

    if "error" in data:
        return TokenError(data.get("error"), data.get("error_description"), resp.status_code, data)

    return TokenSuccess(data)


def fetch_user_info(base_url: str, bearer: str, timeout: float = 10.0) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/GetUserInfo", headers={"Authorization": bearer}, timeout=timeout)
    except requests.RequestException as e:
        return None, f"Request failed: {e}"

    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"

    try:
        data = resp.json()
    except ValueError:
        return None, "Invalid JSON from GetUserInfo"

    if not isinstance(data, dict):
        return None, "Unexpected payload shape for user info"

    return data, None


def fetch_meters(base_url: str, bearer: str, timeout: float = 10.0) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/Meters", headers={"Authorization": bearer}, timeout=timeout)
    except requests.RequestException as e:
        return None, f"Request failed: {e}"

    if resp.status_code != 200:
        return None, f"HTTP {resp.status_code}"

    try:
        data = resp.json()
    except ValueError:
        return None, "Invalid JSON from Meters"

    if not isinstance(data, dict):
        return None, "Unexpected meters payload shape"

    err_msg = data.get("errorMessage") or {}
    if any(err_msg.get(k) for k in ("ErrorType", "UserMessage", "InternalMessage")):
        parts = []
        if err_msg.get("ErrorType"):
            parts.append(f"ErrorType: {err_msg.get('ErrorType')}")
        if err_msg.get("UserMessage"):
            parts.append(f"UserMessage: {err_msg.get('UserMessage')}")
        if err_msg.get("InternalMessage"):
            parts.append(f"InternalMessage: {err_msg.get('InternalMessage')}")
        return None, "; ".join(parts)

    return data, None
