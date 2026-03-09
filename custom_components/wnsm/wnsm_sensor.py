import logging
from datetime import datetime
from typing import Any, Optional

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    ENTITY_ID_FORMAT,
)
from homeassistant.components.sensor import SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.util import slugify

from .AsyncSmartmeter import AsyncSmartmeter
from .api import Smartmeter
from .api.constants import ValueType
from .importer import Importer
from .utils import before, today

_LOGGER = logging.getLogger(__name__)


class WNSMSensor(SensorEntity):
    """
    Home Assistant sensor representing a Wiener Netze Smart Meter Zählpunkt.

    The sensor exposes the absolute cumulative meter reading (kWh) as its
    native value with state_class=TOTAL_INCREASING. This allows HA to track
    incremental consumption automatically and makes the sensor selectable as
    an energy source in the Energy Dashboard – including cost calculation.

    On each update the Importer backfills any missing historical statistics
    using async_import_statistics (source="homeassistant") so that the Energy
    Dashboard has full historical data for cost analysis.
    """

    def _icon(self) -> str:
        return "mdi:flash"

    def __init__(self, username: str, password: str, zaehlpunkt: str) -> None:
        super().__init__()
        self.username = username
        self.password = password
        self.zaehlpunkt = zaehlpunkt

        self._attr_native_value: float | None = None
        self._attr_extra_state_attributes: dict[str, Any] = {}
        self._attr_name = zaehlpunkt
        self._attr_icon = self._icon()
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._attr_device_class = SensorDeviceClass.ENERGY
        self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR

        self._name: str = zaehlpunkt
        self._available: bool = True
        self._updatets: str | None = None

    @property
    def get_state(self) -> Optional[str]:
        if self._attr_native_value is None:
            return None
        return f"{self._attr_native_value:.3f}"

    @property
    def _id(self):
        return ENTITY_ID_FORMAT.format(slugify(self._name).lower())

    @property
    def icon(self) -> str:
        return self._attr_icon

    @property
    def name(self) -> str:
        return self._name

    @property
    def unique_id(self) -> str:
        return self.zaehlpunkt

    @property
    def available(self) -> bool:
        return self._available

    def granularity(self) -> ValueType:
        return ValueType.from_str(
            self._attr_extra_state_attributes.get("granularity", "QUARTER_HOUR")
        )

    async def async_update(self):
        """
        Fetch the latest meter reading and backfill historical statistics.

        The sensor state is set to the most recent available absolute meter
        reading (yesterday's or day-before-yesterday's), which is the cumulative
        kWh since meter installation. This value is consistent with the
        'sum' baseline used in the imported statistics.
        """
        try:
            smartmeter = Smartmeter(username=self.username, password=self.password)
            async_smartmeter = AsyncSmartmeter(self.hass, smartmeter)
            await async_smartmeter.login()

            zaehlpunkt_response = await async_smartmeter.get_zaehlpunkt(self.zaehlpunkt)
            self._attr_extra_state_attributes = zaehlpunkt_response

            if async_smartmeter.is_active(zaehlpunkt_response):
                # Try yesterday first, fall back to the day before yesterday
                # because the API may not have yesterday's reading yet.
                reading_dates = [before(today(), 1), before(today(), 2)]
                for reading_date in reading_dates:
                    meter_reading = await async_smartmeter.get_meter_reading_from_historic_data(
                        self.zaehlpunkt, reading_date, datetime.now()
                    )
                    if meter_reading is not None:
                        self._attr_native_value = meter_reading
                        break

                # Backfill / extend historical statistics.
                # entity_id is passed so the Importer uses source="homeassistant"
                # with the correct statistic_id, enabling Energy Dashboard cost
                # calculation for this sensor.
                importer = Importer(
                    hass=self.hass,
                    async_smartmeter=async_smartmeter,
                    zaehlpunkt=self.zaehlpunkt,
                    unit_of_measurement=self.unit_of_measurement,
                    entity_id=self.entity_id,
                    granularity=self.granularity(),
                )
                await importer.async_import()

            self._available = True
            self._updatets = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        except TimeoutError as e:
            self._available = False
            _LOGGER.warning("Timeout fetching smart meter data: %s", e)
        except RuntimeError as e:
            self._available = False
            _LOGGER.exception("Error fetching smart meter data: %s", e)
