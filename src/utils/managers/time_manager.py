"""
Unified class for time management in FastAPI Template system.
Provides forced UTC formatting and convenient methods for timezone handling.
"""

import logging
from datetime import datetime, time, timedelta
from typing import Optional, Tuple, Union

import pytz

logger = logging.getLogger(__name__)

LOCAL_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"
UTC_ISO_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
UTC_ISO_FORMAT_WITHOUT_MICROSECONDS = "%Y-%m-%dT%H:%M:%SZ"

DATETIME_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d.%m.%Y %H:%M:%S",
    "%d.%m.%Y",
]

TIME_FORMATS = [
    "%H:%M:%S",
    "%H:%M",
]


class TimeManager:
    """
    Unified class for time management in the system.

    Provides:
    - Forced UTC formatting
    - Conversion between timezones
    - Parsing of various date formats
    - Time data validation
    - Convenient methods for working with time ranges
    """

    def __init__(self, default_timezone: str = "Asia/Yekaterinburg"):
        """
        Initialize TimeManager.

        Args:
            default_timezone: Default timezone for conversion.
        """
        self.default_timezone = default_timezone
        self.default_tz = pytz.timezone(default_timezone)

    # ==================== MAIN UTC METHODS ====================

    def force_utc_datetime(
        self, dt: Optional[Union[datetime, str]]
    ) -> Optional[datetime]:
        """
        Force convert datetime to UTC format.

        Args:
            dt: datetime object or string with date/time

        Returns:
            datetime object in UTC or None if input value is None

        Raises:
            ValueError: if date cannot be parsed
            TypeError: if invalid data type is passed
        """

        if dt is None:
            return None

        if isinstance(dt, str):
            dt = self.parse_datetime(dt)

        if not isinstance(dt, datetime):
            raise TypeError(f"Expected datetime or str, got: {type(dt)}")

        if (
            dt.tzinfo is not None
            and dt.utcoffset() is not None
            and dt.utcoffset().total_seconds() == 0
        ):
            return dt

        if dt.tzinfo is None:
            dt = self.default_tz.localize(dt)

        result = dt.astimezone(pytz.UTC)
        return result

    def force_utc_time(self, t: Optional[Union[str, time]]) -> Optional[time]:
        """
        Convert time to UTC format (for Time fields).
        For Time fields, simply return time as is, since they don't contain timezone.

        Args:
            t: time object or string with time

        Returns:
            time object or None

        Raises:
            ValueError: if time cannot be parsed
        """
        if t is None:
            return None

        if isinstance(t, str):
            return self.parse_time(t)

        return t

    def get_utc_now(self) -> datetime:
        """
        Get current time in UTC.

        Returns:
            datetime in UTC
        """
        return datetime.now(pytz.UTC)

    def validate_utc_datetime(self, dt: datetime, field_name: str = "datetime") -> None:
        """
        Validate that datetime is in UTC.

        Args:
            dt: datetime to validate
            field_name: field name for error message

        Raises:
            ValueError: if datetime is not in UTC
        """
        if dt is None:
            return

        if dt.tzinfo is None:
            raise ValueError(
                f"Field {field_name} must be in UTC format. "
                f"Got: {dt} without timezone"
            )

        utc_offset = dt.utcoffset()
        if utc_offset is None or utc_offset.total_seconds() != 0:
            raise ValueError(
                f"Field {field_name} must be in UTC format. "
                f"Got: {dt} with timezone {dt.tzinfo}"
            )

    def ensure_utc_datetime_field(
        self, dt: Optional[datetime], field_name: str = "datetime"
    ) -> Optional[datetime]:
        """
        Ensure that datetime field is in UTC format.
        If not - converts to UTC with logging.

        Args:
            dt: datetime to check/convert
            field_name: field name for logging

        Returns:
            datetime in UTC format or None
        """

        if dt is None:
            return None

        if dt.tzinfo is None:
            logger.warning(
                f"Field {field_name} without timezone: {dt}. "
                f"Automatic conversion to UTC."
            )
            result = self.force_utc_datetime(dt)
            return result

        utc_offset = dt.utcoffset()

        if utc_offset is None or utc_offset.total_seconds() != 0:
            logger.warning(
                f"Field {field_name} not in UTC format: {dt} (timezone: {dt.tzinfo}). "
                f"Automatic conversion to UTC."
            )
            result = self.force_utc_datetime(dt)
            return result

        return dt

    # ==================== PARSING ====================

    def parse_datetime(self, date_str: str) -> datetime:
        """
        Parse string to datetime with support for various formats.

        Args:
            date_str: string with date

        Returns:
            datetime object in UTC

        Raises:
            ValueError: if date cannot be parsed
        """

        if not date_str:
            raise ValueError("Empty date string")

        date_str = date_str.strip()

        if "%3A" in date_str:
            date_str = date_str.replace("%3A", ":")

        for fmt in DATETIME_FORMATS + ["%Y-%m-%dT%H:%M:%S"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt
            except ValueError:
                continue

        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt
        except ValueError as e:
            try:
                if "T" in date_str:
                    date_part, time_part = date_str.split("T")
                    year, month, day = map(int, date_part.split("-"))

                    if ":" in time_part:
                        time_parts = time_part.split(":")
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = (
                            int(time_parts[2].split(".")[0].split("Z")[0].split("+")[0])
                            if len(time_parts) > 2
                            else 0
                        )

                        dt = datetime(year, month, day, hour, minute, second)
                        return dt

                raise ValueError(
                    f"Failed to parse date after all attempts: {date_str}"
                )
            except Exception as e2:
                raise ValueError(
                    f"Failed to parse date: {date_str}. Error: {str(e2)}"
                )

    def parse_time(self, time_str: str) -> time:
        """
        Parse string to time object.

        Args:
            time_str: string with time

        Returns:
            time object

        Raises:
            ValueError: if time cannot be parsed
        """
        if not time_str:
            raise ValueError("Empty time string")

        time_str = time_str.strip()

        for fmt in TIME_FORMATS:
            try:
                return datetime.strptime(time_str, fmt).time()
            except ValueError:
                continue

        raise ValueError(f"Failed to parse time: {time_str}")

    def parse_datetime_flexible(self, date_str: str) -> datetime:
        """
        Flexible datetime parser (alias for parse_datetime for backward compatibility).

        Args:
            date_str: string with date

        Returns:
            datetime object without timezone (naive time)
        """

        if "%3A" in date_str:
            date_str = date_str.replace("%3A", ":")

        try:
            result = self.parse_datetime(date_str)
            return result
        except ValueError as e:
            try:
                if "T" in date_str:
                    date_part, time_part = date_str.split("T")
                    year, month, day = map(int, date_part.split("-"))

                    if ":" in time_part:
                        time_parts = time_part.split(":")
                        hour = int(time_parts[0])
                        minute = int(time_parts[1])
                        second = (
                            int(time_parts[2].split(".")[0].split("Z")[0].split("+")[0])
                            if len(time_parts) > 2
                            else 0
                        )

                        dt = datetime(year, month, day, hour, minute, second)
                        return dt

                for fmt in DATETIME_FORMATS + ["%Y-%m-%dT%H:%M:%S"]:
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt
                    except ValueError:
                        continue

                raise ValueError(
                    f"Failed to parse date after all attempts: {date_str}"
                )
            except Exception as e2:
                raise ValueError(
                    f"Failed to parse date: {date_str}. Error: {str(e2)}"
                )

    # ==================== TIMEZONE CONVERSION ====================

    def convert_utc_to_local_time(self, utc_time: datetime, time_zone: str) -> datetime:
        """
        Convert UTC time to user local time.

        Args:
            utc_time: datetime in UTC
            time_zone: user timezone

        Returns:
            datetime in local timezone
        """

        # Ensure time is in UTC
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=pytz.UTC)
        elif utc_time.utcoffset() is None or utc_time.utcoffset().total_seconds() != 0:
            utc_time = utc_time.astimezone(pytz.UTC)

        user_tz = pytz.timezone(time_zone)

        result = utc_time.astimezone(user_tz)
        return result

    def convert_to_utc(
        self, start, end, timezone_str: str = None
    ) -> Tuple[datetime, datetime]:
        """
        Convert local time to UTC.

        Args:
            start: start time (datetime or string)
            end: end time (datetime or string)
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            tuple (start_utc, end_utc)
        """

        if isinstance(start, str):
            start = self.parse_datetime_flexible(start)

        if isinstance(end, str):
            end = self.parse_datetime_flexible(end)

        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)

        if start.tzinfo is None:
            start = tz.localize(start)
        elif start.utcoffset() is not None and start.utcoffset().total_seconds() == 0:
            start_local = start.astimezone(tz)
            start = start_local
        else:
            start = start.astimezone(tz)

        if end.tzinfo is None:
            end = tz.localize(end)
        elif end.utcoffset() is not None and end.utcoffset().total_seconds() == 0:
            end_local = end.astimezone(tz)
            end = end_local
        else:
            end = end.astimezone(tz)

        start_utc = start.astimezone(pytz.UTC)
        end_utc = end.astimezone(pytz.UTC)

        return start_utc, end_utc

    def get_timezone_offset(self, timezone_str: str = None) -> int:
        """
        Get timezone offset in hours.

        Args:
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            offset in hours
        """

        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        offset_seconds = now.utcoffset().total_seconds()
        offset_hours = int(offset_seconds / 3600)

        return offset_hours

    # ==================== TIME RANGES ====================

    def get_today_range(self, timezone_str: str = None) -> Tuple[datetime, datetime]:
        """
        Get today's time range in UTC.

        Args:
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            tuple (start_utc, end_utc)
        """
        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        return start.astimezone(pytz.UTC), end.astimezone(pytz.UTC)

    def get_yesterday_range(
        self, timezone_str: str = None
    ) -> Tuple[datetime, datetime]:
        """
        Get yesterday's time range in UTC.

        Args:
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            tuple (start_utc, end_utc)
        """
        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        start = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=1)

        return start.astimezone(pytz.UTC), end.astimezone(pytz.UTC)

    def get_lastmonth_range(
        self, timezone_str: str = None
    ) -> Tuple[datetime, datetime]:
        """
        Get last month's time range in UTC.

        Args:
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            tuple (start_utc, end_utc)
        """
        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        start = (now - timedelta(days=30)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)

        return start.astimezone(pytz.UTC), end.astimezone(pytz.UTC)

    def get_week_range(self, timezone_str: str = None) -> Tuple[datetime, datetime]:
        """
        Get current week's time range in UTC.

        Args:
            timezone_str: timezone (if None, uses default_timezone)

        Returns:
            tuple (start_utc, end_utc)
        """
        if timezone_str is None:
            timezone_str = self.default_timezone

        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)
        start = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        end = start + timedelta(days=7)

        return start.astimezone(pytz.UTC), end.astimezone(pytz.UTC)

    # ==================== FORMATTING ====================

    def format_datetime_to_str(
        self, dt_start: datetime, dt_end: datetime
    ) -> Tuple[str, str]:
        """
        Convert datetime to UTC format strings.

        Args:
            dt_start: start time
            dt_end: end time

        Returns:
            tuple (start_str, end_str)
        """

        dt_start = self.ensure_utc_datetime_field(dt_start, "dt_start")
        dt_end = self.ensure_utc_datetime_field(dt_end, "dt_end")

        try:
            start_str = dt_start.strftime(UTC_ISO_FORMAT_WITHOUT_MICROSECONDS)
            end_str = dt_end.strftime(UTC_ISO_FORMAT_WITHOUT_MICROSECONDS)
            return start_str, end_str
        except Exception as e:
            try:
                start_str = f"{dt_start.year}-{dt_start.month:02d}-{dt_start.day:02d}T{dt_start.hour:02d}:{dt_start.minute:02d}:{dt_start.second:02d}Z"
                end_str = f"{dt_end.year}-{dt_end.month:02d}-{dt_end.day:02d}T{dt_end.hour:02d}:{dt_end.minute:02d}:{dt_end.second:02d}Z"
                return start_str, end_str
            except Exception as e2:
                raise

    def format_datetime_rabbit(self, dt: datetime) -> str:
        """
        Format datetime to string for RabbitMQ.

        Args:
            dt: datetime to format

        Returns:
            string in format '%Y-%m-%dT%H:%M:%S.%fZ'
        """
        return dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def format_mmss(self, val: float) -> str:
        """
        Format time in minutes to MM:SS format.

        Args:
            val: time in minutes (can be fractional)

        Returns:
            string in MM:SS format
        """
        mins = int(val)
        secs = int(round((val - mins) * 60))
        return f"{mins:02}:{secs:02}"

    # ==================== UTILITIES ====================

    def get_aggregate_interval(self, start: datetime, end: datetime) -> str:
        """
        Determine aggregation interval based on time range.

        Args:
            start: start time
            end: end time

        Returns:
            string with aggregation interval
        """
        delta = end - start
        total_hours = delta.total_seconds() / 3600

        if total_hours <= 1:
            return "2s"
        elif total_hours <= 3:
            return "5s"
        elif total_hours <= 6:
            return "10s"
        elif total_hours <= 24:
            return "60s"
        elif total_hours <= 168:
            return "600s"
        else:
            return "1h"

    def is_utc(self, dt: datetime) -> bool:
        """
        Check if datetime is UTC.

        Args:
            dt: datetime to check

        Returns:
            True if datetime is in UTC, False otherwise
        """
        return (
            dt.tzinfo is not None
            and dt.utcoffset() is not None
            and dt.utcoffset().total_seconds() == 0
        )

    def is_naive(self, dt: datetime) -> bool:
        """
        Check if datetime is naive (without timezone).

        Args:
            dt: datetime to check

        Returns:
            True if datetime is naive, False otherwise
        """
        return dt.tzinfo is None

    def ensure_utc_datetime(self, dt: datetime) -> datetime:
        """
        Ensure that datetime is in UTC (alias for ensure_utc_datetime_field).

        Args:
            dt: datetime to check/convert

        Returns:
            datetime in UTC
        """
        return self.ensure_utc_datetime_field(dt, "datetime")

    def convert_utc_strings_to_local_strings(
        self, start_str: str, end_str: str, time_zone: str
    ) -> tuple[str, str]:
        """
        Convert time strings from UTC to local time.

        Args:
            start_str: start time string in UTC format
            end_str: end time string in UTC format
            time_zone: target timezone

        Returns:
            tuple[str, str]: tuple of time strings in local format
        """
        start_utc = self.parse_datetime_flexible(start_str)
        end_utc = self.parse_datetime_flexible(end_str)

        start_local = self.convert_utc_to_local_time(start_utc, time_zone)
        end_local = self.convert_utc_to_local_time(end_utc, time_zone)

        start_local_str = start_local.strftime(UTC_ISO_FORMAT_WITHOUT_MICROSECONDS)
        end_local_str = end_local.strftime(UTC_ISO_FORMAT_WITHOUT_MICROSECONDS)

        return start_local_str, end_local_str

    def convert_local_strings_to_utc_strings(
        self, start: str, end: str
    ) -> Tuple[str, str]:
        """
        Convert time strings from local time to UTC format.
        """
        start_local = self.parse_datetime_flexible(start)
        end_local = self.parse_datetime_flexible(end)

        start_utc, end_utc = self.convert_to_utc(start_local, end_local)

        return start_utc.strftime(
            UTC_ISO_FORMAT_WITHOUT_MICROSECONDS
        ), end_utc.strftime(UTC_ISO_FORMAT_WITHOUT_MICROSECONDS)


time_manager = TimeManager()


def force_utc_datetime(dt: Optional[Union[datetime, str]]) -> Optional[datetime]:
    """Alias for time_manager.force_utc_datetime."""
    return time_manager.force_utc_datetime(dt)


def force_utc_time(t: Optional[Union[str, time]]) -> Optional[time]:
    """Alias for time_manager.force_utc_time."""
    return time_manager.force_utc_time(t)


def get_utc_now() -> datetime:
    """Alias for time_manager.get_utc_now."""
    return time_manager.get_utc_now()


def validate_utc_datetime(dt: datetime, field_name: str = "datetime") -> None:
    """Alias for time_manager.validate_utc_datetime."""
    return time_manager.validate_utc_datetime(dt, field_name)


def ensure_utc_datetime_field(
    dt: Optional[datetime], field_name: str = "datetime"
) -> Optional[datetime]:
    """Alias for time_manager.ensure_utc_datetime_field."""
    return time_manager.ensure_utc_datetime_field(dt, field_name)


def parse_datetime_flexible(date_str: str) -> datetime:
    """Alias for time_manager.parse_datetime_flexible."""
    return time_manager.parse_datetime_flexible(date_str)


def convert_utc_to_local_time(local_time: datetime, time_zone: str):
    """Alias for time_manager.convert_utc_to_local_time."""
    return time_manager.convert_utc_to_local_time(local_time, time_zone)


def convert_to_utc(
    start: datetime, end: datetime, timezone_str: str = "Asia/Yekaterinburg"
):
    """Alias for time_manager.convert_to_utc."""
    return time_manager.convert_to_utc(start, end, timezone_str)


def get_timezone_offset(timezone_str: str = "Asia/Yekaterinburg") -> int:
    """Alias for time_manager.get_timezone_offset."""
    return time_manager.get_timezone_offset(timezone_str)


def ensure_utc_datetime(dt: datetime) -> datetime:
    """Alias for time_manager.ensure_utc_datetime."""
    return time_manager.ensure_utc_datetime(dt)


def parse_datetime_to_str(dt_start: datetime, dt_end: datetime):
    """Alias for time_manager.format_datetime_to_str."""
    return time_manager.format_datetime_to_str(dt_start, dt_end)


def get_yesterday_range(timezone_str: str):
    """Alias for time_manager.get_yesterday_range."""
    return time_manager.get_yesterday_range(timezone_str)


def get_today_range(timezone_str: str):
    """Alias for time_manager.get_today_range."""
    return time_manager.get_today_range(timezone_str)


def get_lastmonth_range(timezone_str: str):
    """Alias for time_manager.get_lastmonth_range."""
    return time_manager.get_lastmonth_range(timezone_str)


def get_aggregate_interval(start: datetime, end: datetime) -> str:
    """Alias for time_manager.get_aggregate_interval."""
    return time_manager.get_aggregate_interval(start, end)


def convert_utc_strings_to_local_strings(
    start_str: str, end_str: str, time_zone: str
) -> tuple[str, str]:
    """Alias for time_manager.convert_utc_strings_to_local_strings."""
    return time_manager.convert_utc_strings_to_local_strings(
        start_str, end_str, time_zone
    )


def format_mmss(val: float) -> str:
    """Alias for time_manager.format_mmss."""
    return time_manager.format_mmss(val)


def format_datetime_rabbit(dt: datetime) -> str:
    """Alias for time_manager.format_datetime_rabbit."""
    return time_manager.format_datetime_rabbit(dt)
