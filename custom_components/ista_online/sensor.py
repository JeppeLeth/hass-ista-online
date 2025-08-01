from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from .const import DOMAIN
from typing import Any, Optional
from datetime import datetime, timezone
import re

DIAGNOSTIC_FIELDS = {
    "Activation date": "Activation_date",
    "Deactivation date": "Deactivation_date",
    "Message": "Message",
    "Headline": "Headline",
    "Meter type": "MeterType",
    "Meter code": "METTYPE_CODE",
    "Meter text": "MeterText",
    "Reading date": "Reading_date",
}

USER_INFO_DIAGNOSTIC_FIELDS = {
    "Address Street": "Address",
    "Address Zip": "ZipCity",
}



def _map_device_class(meter_type: Any):
    mt = (str(meter_type) if meter_type else "").upper()
    if mt in ("CW", "HW"):
        return SensorDeviceClass.WATER
    if mt == "ENERGY":
        return SensorDeviceClass.ENERGY
    if mt == "ELECTRICITY":
        return SensorDeviceClass.ENERGY
    return None


def _normalize_unit(unit: Any) -> Any:
    if isinstance(unit, str):
        if unit.lower() == "m3":
            return "m³"
        if unit.lower() == "kwh":
            return "kWh"
    return unit

def _suggest_precision_for_unit(native_unit: str | None) -> int | None:
    """Return suggested precision for known units."""
    if native_unit == "m³":
        return 3
    return None


def _parse_date_string(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        # Reading_date is in format "23-07-2025"
        if re.match(r"\d{2}-\d{2}-\d{4}$", value.strip()):
            dt = datetime.strptime(value.strip(), "%d-%m-%Y")
            return dt.replace(tzinfo=timezone.utc)
        s = value.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


class MeterSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter: dict, user_info: dict):
        super().__init__(coordinator)
        self._meter = meter or {}
        self._user_info = user_info or {}
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        self._unique_id = f"ista_meter_{serial}_last_meter_reading"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return "Last Meter Reading"

    @property
    def native_value(self) -> Any:
        return self._meter.get("Last_Meter_Reading")

    @property
    def native_unit_of_measurement(self) -> Any:
        return _normalize_unit(self._meter.get("Unit"))
    
    @property
    def native_precision(self) -> int | None:
        return _suggest_precision_for_unit(self.native_unit_of_measurement)

    @property
    def device_class(self):
        return _map_device_class(self._meter.get("MeterType"))

    @property
    def state_class(self) -> str:
        return "total"

    @property
    def device_info(self) -> DeviceInfo:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        model = self._meter.get("METCAT_LABEL") or ""
        return DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            manufacturer="ISTA",
            serial_number=serial,
            name=f"Meter {serial}",
            model=model,
        )

    @property
    def extra_state_attributes(self) -> dict:
        attrs = {
            "address": self._user_info.get("Address"),
            "city": self._user_info.get("ZipCity"),
            "room_description": self._meter.get("ROOM_DESCR"),
        }
        return {k: v for k, v in attrs.items() if v is not None}

    def _handle_coordinator_update(self) -> None:
        meters = self.coordinator.data.get("meters", {}) or {}
        meters_value = (meters.get("Meters") or {}).get("Value") or []
        for m in meters_value:
            if str(m.get("METER_ID")) == str(self._meter.get("METER_ID")):
                self._meter = m
                break
        self.async_write_ha_state()


class MeterConsumptionSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter: dict, user_info: dict):
        super().__init__(coordinator)
        self._meter = meter or {}
        self._user_info = user_info or {}
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        self._unique_id = f"ista_meter_{serial}_last_meter_consumption"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        return "Last Meter Consumption"

    @property
    def native_value(self) -> Any:
        return self._meter.get("Last_Meter_Consumption")

    @property
    def native_unit_of_measurement(self) -> Any:
        return _normalize_unit(self._meter.get("Unit"))

    @property
    def native_precision(self) -> int | None:
        return _suggest_precision_for_unit(self.native_unit_of_measurement)

    @property
    def device_class(self):
        return _map_device_class(self._meter.get("MeterType"))

    @property
    def state_class(self) -> str:
        return "total_increasing"

    @property
    def device_info(self) -> DeviceInfo:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        model = self._meter.get("METCAT_LABEL") or ""
        return DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            manufacturer="ISTA",
            serial_number=serial,
            name=f"Meter {serial}",
            model=model,
        )

    @property
    def extra_state_attributes(self) -> dict:
        attrs = {
            "address": self._user_info.get("Address"),
            "city": self._user_info.get("ZipCity"),
        }
        return {k: v for k, v in attrs.items() if v is not None}

    def _handle_coordinator_update(self) -> None:
        meters = self.coordinator.data.get("meters", {}) or {}
        meters_value = (meters.get("Meters") or {}).get("Value") or []
        for m in meters_value:
            if str(m.get("METER_ID")) == str(self._meter.get("METER_ID")):
                self._meter = m
                break
        self.async_write_ha_state()


class MeterDiagnosticSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter: dict, user_info: dict, display_name: str, field_key: str):
        super().__init__(coordinator)
        self._meter = meter or {}
        self._user_info = user_info or {}
        self._field_key = field_key
        self._display_name = display_name
        self._unique_id = f"{self._meter.get('METER_ID')}_{field_key}"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        return f"Meter {serial} {self._display_name}"

    @property
    def native_value(self) -> Any:
        # parse dates for certain fields
        if self._field_key in ("Reading_date", "Activation_date", "Deactivation_date"):
            dt = _parse_date_string(self._meter.get(self._field_key))
            if dt:
                return dt.isoformat()
        return self._meter.get(self._field_key)

    @property
    def native_unit_of_measurement(self) -> Any:
        return None

    @property
    def device_class(self) -> Optional[str]:
        if self._field_key in ("Reading_date", "Activation_date", "Deactivation_date"):
            return None
        return None

    @property
    def entity_category(self) -> Any:
        return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> DeviceInfo:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        model = self._meter.get("METCAT_LABEL") or ""
        return DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            manufacturer="ISTA",
            serial_number=serial,
            name=f"Meter {serial}",
            model=model,
        )

    def _handle_coordinator_update(self) -> None:
        meters = self.coordinator.data.get("meters", {}) or {}
        meters_value = (meters.get("Meters") or {}).get("Value") or []
        for m in meters_value:
            if str(m.get("METER_ID")) == str(self._meter.get("METER_ID")):
                self._meter = m
                break
        self.async_write_ha_state()


class UserInfoDiagnosticSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, meter: dict, user_info: dict, display_name: str, user_field_key: str):
        super().__init__(coordinator)
        self._meter = meter or {}
        self._user_info = user_info or {}
        self._display_name = display_name
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        key = user_field_key.lower().replace(" ", "_")
        self._field_key = user_field_key
        self._unique_id = f"ista_meter_{serial}_{key}"

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def name(self) -> str:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        return f"Meter {serial} {self._display_name}"

    @property
    def native_value(self) -> Any:
        return self._user_info.get(self._field_key)

    @property
    def native_unit_of_measurement(self) -> Any:
        return None

    @property
    def entity_category(self) -> Any:
        return EntityCategory.DIAGNOSTIC

    @property
    def device_info(self) -> DeviceInfo:
        serial = self._meter.get("METER_NO") or self._meter.get("METER_ID")
        model = self._meter.get("METCAT_LABEL") or ""
        return DeviceInfo(
            identifiers={(DOMAIN, str(serial))},
            manufacturer="ISTA",
            serial_number=serial,
            name=f"Meter {serial}",
            model=model,
        )

    def _handle_coordinator_update(self) -> None:
        # nothing special; just refresh
        self.async_write_ha_state()


async def async_setup_entry(hass, entry, async_add_entities):
    from .const import DOMAIN  # avoid circular if needed
    coordinator = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not coordinator:
        return
    meters = (coordinator.data.get("meters") or {}).get("Meters", {}).get("Value", [])
    user_info = coordinator.data.get("user_info", {})
    entities = []
    for m in meters:
        entities.append(MeterSensor(coordinator, m, user_info))
        entities.append(MeterConsumptionSensor(coordinator, m, user_info))
        for display_name, key in DIAGNOSTIC_FIELDS.items():
            entities.append(MeterDiagnosticSensor(coordinator, m, user_info, display_name, key))
        for display_name, key in USER_INFO_DIAGNOSTIC_FIELDS.items():
            entities.append(UserInfoDiagnosticSensor(coordinator, m, user_info, display_name, key))
    async_add_entities(entities, True)
