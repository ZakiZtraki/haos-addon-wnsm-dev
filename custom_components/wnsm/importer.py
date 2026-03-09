"""
Statistics importer for Wiener Netze Smart Meter data.

Key design: Uses async_import_statistics (source="homeassistant") so that
imported statistics are tied to the sensor entity. This enables the Home
Assistant Energy Dashboard to use the sensor for cost calculation, which
requires entity-based statistics rather than external statistics.

Historical data is fetched from the bewegungsdaten API and backfilled into
the HA statistics table. The running sum is initialized from the actual meter
reading at the start of the import period so that statistics are consistent
with the sensor's native value (absolute cumulative kWh).
"""
import logging
from collections import defaultdict
from datetime import timedelta, timezone, datetime
from decimal import Decimal
from operator import itemgetter

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import (
    StatisticData,
    StatisticMetaData,
)
from homeassistant.components.recorder.statistics import (
    get_last_statistics,
    async_import_statistics,
)
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .AsyncSmartmeter import AsyncSmartmeter
from .api.constants import ValueType
from .utils import before, today

_LOGGER = logging.getLogger(__name__)

# How far back to fetch historical data on first import
HISTORY_YEARS = 3


class Importer:
    """
    Imports Wiener Netze bewegungsdaten into HA long-term statistics.

    Statistics are stored with source="homeassistant" and a statistic_id
    matching the sensor entity_id (e.g. "sensor.at001..."). This makes them
    available as entity-based statistics which support cost calculation in the
    Energy Dashboard.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        async_smartmeter: AsyncSmartmeter,
        zaehlpunkt: str,
        unit_of_measurement: str,
        entity_id: str,
        granularity: ValueType = ValueType.QUARTER_HOUR,
    ):
        # Use the sensor entity_id as statistic_id so HA links the statistics
        # to the real sensor entity, enabling Energy Dashboard cost calculation.
        self.id = entity_id
        self.zaehlpunkt = zaehlpunkt
        self.granularity = granularity
        self.unit_of_measurement = unit_of_measurement
        self.hass = hass
        self.async_smartmeter = async_smartmeter

    def is_last_inserted_stat_valid(self, last_inserted_stat):
        return (
            len(last_inserted_stat) == 1
            and len(last_inserted_stat[self.id]) == 1
            and "sum" in last_inserted_stat[self.id][0]
            and "end" in last_inserted_stat[self.id][0]
        )

    def prepare_start_off_point(self, last_inserted_stat):
        """Extract the start datetime and last sum from the most recent statistic."""
        _sum = Decimal(last_inserted_stat[self.id][0]["sum"])
        start = last_inserted_stat[self.id][0]["end"]

        # Handle the different return types HA has used over versions
        if isinstance(start, (int, float)):
            start = dt_util.utc_from_timestamp(start)
        if isinstance(start, str):
            start = dt_util.parse_datetime(start)

        if not isinstance(start, datetime):
            _LOGGER.error(
                "Unexpected type for 'end' in last statistic: %s (type: %s). "
                "Please open a bug report.",
                last_inserted_stat,
                type(last_inserted_stat[self.id][0]["end"]),
            )
            return None

        _LOGGER.debug("Resuming import from: %s", start)

        # Don't hit the API if data was imported less than 24 h ago
        min_wait = timedelta(hours=24)
        delta_t = datetime.now(timezone.utc).replace(microsecond=0) - start.replace(microsecond=0)
        if delta_t <= min_wait:
            _LOGGER.debug(
                "Skipping API call - last import was less than 24 h ago. "
                "Next earliest update in %s",
                min_wait - delta_t,
            )
            return None

        return start, _sum

    async def async_import(self):
        """Main entry point: fetch new data and import into HA statistics."""
        last_inserted_stat = await get_instance(self.hass).async_add_executor_job(
            get_last_statistics,
            self.hass,
            1,
            self.id,
            True,
            {"sum", "state"},
        )
        _LOGGER.debug("Last inserted stat: %s", last_inserted_stat)

        try:
            await self.async_smartmeter.login()
            zaehlpunkt_info = await self.async_smartmeter.get_zaehlpunkt(self.zaehlpunkt)

            if not self.async_smartmeter.is_active(zaehlpunkt_info):
                _LOGGER.debug("Smartmeter %s is not active", self.zaehlpunkt)
                return

            if not self.is_last_inserted_stat_valid(last_inserted_stat):
                _LOGGER.warning(
                    "No previous statistics found for %s. "
                    "Starting full historical import (up to %d years). "
                    "This may take a moment.",
                    self.id,
                    HISTORY_YEARS,
                )
                await self._initial_import_statistics()
            else:
                start_off_point = self.prepare_start_off_point(last_inserted_stat)
                if start_off_point is None:
                    return
                start, _sum = start_off_point
                await self._incremental_import_statistics(start, _sum)

        except TimeoutError as e:
            _LOGGER.warning("Timeout fetching smart meter data: %s", e)
        except RuntimeError as e:
            _LOGGER.exception("Error fetching smart meter data: %s", e)

    def get_statistics_metadata(self) -> StatisticMetaData:
        """
        Return metadata for async_import_statistics.

        source="homeassistant" links these statistics to the sensor entity
        identified by statistic_id (= entity_id). This is required for the
        Energy Dashboard cost calculation feature.
        """
        return StatisticMetaData(
            source="homeassistant",
            statistic_id=self.id,
            name=self.zaehlpunkt,
            unit_of_measurement=self.unit_of_measurement,
            has_mean=False,
            has_sum=True,
        )

    async def _get_initial_meter_reading(self, start: datetime) -> Decimal:
        """
        Fetch the absolute meter reading at the start of the import window.

        Initialising the running sum from the actual meter reading ensures that
        statistics are consistent with the sensor's native value (which also
        reflects the absolute cumulative reading). Without this, there would be
        a discontinuity between historical imported stats and the real-time
        sensor state when the Energy Dashboard calculates costs.
        """
        try:
            reading = await self.async_smartmeter.get_meter_reading_from_historic_data(
                self.zaehlpunkt,
                start,
                start + timedelta(days=7),
            )
            if reading is not None:
                _LOGGER.debug(
                    "Using initial meter reading of %.3f kWh at %s as sum baseline",
                    reading,
                    start,
                )
                return Decimal(str(reading))
        except Exception as e:
            _LOGGER.warning(
                "Could not fetch initial meter reading for sum baseline: %s. "
                "Defaulting sum to 0.",
                e,
            )
        return Decimal(0)

    async def _initial_import_statistics(self):
        start = (
            datetime.now(timezone.utc)
            .replace(hour=0, minute=0, second=0, microsecond=0)
            - timedelta(days=365 * HISTORY_YEARS)
        )
        initial_sum = await self._get_initial_meter_reading(start)
        return await self._import_statistics(start=start, total_usage=initial_sum)

    async def _incremental_import_statistics(self, start: datetime, total_usage: Decimal):
        return await self._import_statistics(start=start, total_usage=total_usage)

    async def _import_statistics(
        self,
        start: datetime = None,
        end: datetime = None,
        total_usage: Decimal = Decimal(0),
    ):
        """Fetch bewegungsdaten from the API and write them into HA statistics."""
        if start is None:
            start = (
                datetime.now(timezone.utc)
                .replace(hour=0, minute=0, second=0, microsecond=0)
                - timedelta(days=365 * HISTORY_YEARS)
            )
        if end is None:
            end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        if start.tzinfo is None:
            raise ValueError("start datetime must be timezone-aware")

        _LOGGER.debug("Importing statistics from %s to %s", start, end)

        if start > end:
            _LOGGER.warning(
                "start (%s) is after end (%s) – skipping import", start, end
            )
            return total_usage

        bewegungsdaten = await self.async_smartmeter.get_bewegungsdaten(
            self.zaehlpunkt, start, end, self.granularity
        )
        _LOGGER.debug("Bewegungsdaten: %s", bewegungsdaten)

        unit = bewegungsdaten.get('unitOfMeasurement', '')
        if unit == 'WH':
            factor = Decimal('0.001')
        elif unit == 'KWH':
            factor = Decimal('1')
        else:
            raise NotImplementedError(
                f"Unit '{unit}' is not yet implemented. Please report!"
            )

        if 'values' not in bewegungsdaten:
            raise ValueError("WienerNetze did not return any historical values")

        total_consumption = sum(v.get("wert", 0) or 0 for v in bewegungsdaten['values'])
        if total_consumption == 0:
            _LOGGER.debug(
                "No consumption data in batch starting at %s – nothing to import", start
            )
            return total_usage

        # Aggregate quarter-hourly values into hourly buckets
        hourly_buckets: dict[datetime, Decimal] = defaultdict(Decimal)
        last_ts = start

        for value in bewegungsdaten['values']:
            ts = dt_util.parse_datetime(value['zeitpunktVon'])
            if ts is None:
                _LOGGER.warning("Could not parse timestamp: %s", value.get('zeitpunktVon'))
                continue
            if ts < last_ts:
                _LOGGER.warning(
                    "Out-of-order timestamp %s (expected >= %s) – skipping", ts, last_ts
                )
                continue
            last_ts = ts

            wert = value.get('wert')
            if wert is None:
                continue

            reading = Decimal(str(wert)) * factor

            if ts.minute % 15 != 0 or ts.second != 0 or ts.microsecond != 0:
                _LOGGER.warning("Unexpected sub-15-minute timestamp: %s", value)

            if value.get('geschaetzt'):
                _LOGGER.debug("Estimated value at %s: %.4f kWh", ts, reading)

            # Bucket into whole hours
            hourly_buckets[ts.replace(minute=0, second=0, microsecond=0)] += reading

        statistics: list[StatisticData] = []
        metadata = self.get_statistics_metadata()

        for ts, hourly_usage in sorted(hourly_buckets.items(), key=itemgetter(0)):
            total_usage += hourly_usage
            statistics.append(
                StatisticData(
                    start=ts,
                    # state = absolute cumulative reading at this point in time,
                    # consistent with the sensor's native_value (total_increasing).
                    state=float(total_usage),
                    sum=float(total_usage),
                )
            )

        if statistics:
            _LOGGER.debug(
                "Importing %d hourly statistics (%s → %s)",
                len(statistics),
                statistics[0].start,
                statistics[-1].start,
            )
            # async_import_statistics stores data with source="homeassistant"
            # and links it to the sensor entity via statistic_id = entity_id.
            # This enables Energy Dashboard cost calculation.
            async_import_statistics(self.hass, metadata, statistics)
        else:
            _LOGGER.debug("No statistics to import for batch starting at %s", start)

        return total_usage
