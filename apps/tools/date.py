# pylint: disable=signature-differs
# reason: This class adds multiple constructors and overloads the __new__ method to allow for flexible initialization.
# Thus the signature intentionally differs from the parent class.
from datetime import datetime
from typing import Any, Union, overload

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class Date(datetime):
    """
    A subclass of `datetime.datetime` that provides additional functionality for working with dates.

    This class extends the `datetime.datetime` class and adds methods for formatting dates, adding or subtracting time intervals,
    and getting the first or last day of the year.

    Additionally, this class provides support for pydantic serialization and deserialization.

    """

    _spanish_months = {
        1: "Enero",
        2: "Febrero",
        3: "Marzo",
        4: "Abril",
        5: "Mayo",
        6: "Junio",
        7: "Julio",
        8: "Agosto",
        9: "Septiembre",
        10: "Octubre",
        11: "Noviembre",
        12: "Diciembre",
    }

    # Overload for initializing with no arguments
    @overload
    def __new__(cls) -> "Date": ...

    # Overload for initializing with a date string
    @overload
    def __new__(cls, date_str: str) -> "Date": ...

    # Overload for initializing with a datetime object
    @overload
    def __new__(cls, datetime_obj: datetime) -> "Date": ...

    # Overload for initializing with keyword arguments
    @overload
    def __new__(
        cls,
        *,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        fold: int = 0,
    ) -> "Date": ...

    # Overload for initializing with positional arguments
    @overload
    def __new__(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        /,
        fold: int = 0,
    ) -> "Date": ...

    def __new__(
        cls,
        *args: Union[int, str, datetime],
        **kwargs: Union[int, str, datetime],
    ) -> "Date":
        # Handle no arguments
        if len(args) == 0 and len(kwargs) == 0:
            return cls._init_from_datetime(datetime.now())

        # Handle keyword arguments (must not have positional arguments)
        if len(kwargs) > 0:
            if len(args) > 0:
                raise TypeError(
                    "Cannot use both positional and keyword arguments for Date initialization."
                )
            required_keys = {"year", "month", "day"}
            if not required_keys.issubset(kwargs.keys()):
                missing = required_keys - kwargs.keys()
                raise TypeError(f"Missing required keyword arguments: {missing}")

            # Extract keyword arguments with defaults
            year = kwargs.get("year")
            month = kwargs.get("month")
            day = kwargs.get("day")
            hour = kwargs.get("hour", 0)
            minute = kwargs.get("minute", 0)
            second = kwargs.get("second", 0)
            microsecond = kwargs.get("microsecond", 0)
            fold = kwargs.get("fold", 0)

            return cls._init_from_components(year, month, day, hour, minute, second, microsecond, fold)  # type: ignore

        # Handle single argument
        if len(args) == 1:
            if isinstance(args[0], str):
                date_str = args[0]
                return cls._init_from_string(date_str)
            if isinstance(args[0], datetime):
                datetime_obj = args[0]
                return cls._init_from_datetime(datetime_obj)

            raise TypeError(
                "Single positional argument must be a string or datetime object."
            )

        # Handle multiple positional arguments
        if (
            3 <= len(args)
            and len(args) <= 8
            and all(isinstance(arg, int) for arg in args[:-1])
        ):
            # Unpack arguments with defaults
            year = args[0]  # type: ignore
            month = args[1]  # type: ignore
            day = args[2]  # type: ignore
            hour = args[3] if len(args) > 3 else 0
            minute = args[4] if len(args) > 4 else 0
            second = args[5] if len(args) > 5 else 0
            microsecond = args[6] if len(args) > 6 else 0
            fold = kwargs.get("fold", 0)
            return cls._init_from_components(year, month, day, hour, minute, second, microsecond, fold)  # type: ignore

        # If none of the above, raise an error
        raise TypeError(
            "Invalid arguments for Date initialization. "
            "Use either (year: int, month: int, day: int, hour: int = 0, "
            "minute: int = 0, second: int = 0, fold: int = 0), "
            "a date string, keyword arguments, or a datetime object."
        )

    @classmethod
    def _init_from_components(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int,
        minute: int,
        second: int,
        microsecond: int,
        fold: int,
    ) -> "Date":
        # Validate date and time components
        instance = super().__new__(
            cls,
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            None,
            fold=fold,
        )
        return instance

    @classmethod
    def _init_from_string(cls, date_str: str) -> "Date":
        # Define date and datetime formats to parse
        try:
            date = parse(date_str)
            return cls._init_from_datetime(date)
        except ValueError as e:
            raise ValueError("Invalid date string format") from e

    @classmethod
    def _init_from_datetime(cls, datetime_obj: datetime) -> "Date":
        return cls._init_from_components(
            datetime_obj.year,
            datetime_obj.month,
            datetime_obj.day,
            datetime_obj.hour,
            datetime_obj.minute,
            datetime_obj.second,
            datetime_obj.microsecond,
            datetime_obj.fold,
        )

    def __str__(self):
        return self.rfc3339_string

    @property
    def date_string(self):
        """
        Converts the date object to a string representation in the format 'YYYY-MM-DD'.

        Returns:
            str: The date as a string in the format 'YYYY-MM-DD'.
        """
        return self.strftime("%Y-%m-%d")

    @property
    def iso_string(self):
        """
        Returns the ISO 8601 formatted string representation of the date.

        :return: The ISO 8601 formatted string representation of the date.
        :rtype: str
        """
        return self.isoformat()

    @property
    def europe_string(self):
        """
        Returns the date and time in European format (dd/mm/yyyy HH:MM:SS).

        Returns:
            str: The date and time in European format.
        """
        return self.strftime("%d/%m/%Y %H:%M:%S")

    @property
    def rfc2822_string(self):
        """
        Returns the date and time formatted as a string in RFC 2822 format.

        The format of the returned string is: "Day, DD Month YYYY HH:MM:SS",
        where Day is the abbreviated day of the week (e.g., Mon, Tue, etc.),
        DD is the day of the month (e.g., 01, 02, etc.), Month is the abbreviated
        month name (e.g., Jan, Feb, etc.), YYYY is the four-digit year, HH is
        the hour in 24-hour format (e.g., 00, 01, etc.), MM is the minute, and
        SS is the second.

        Returns:
            str: The date and time formatted as a string in RFC 2822 format.
        """
        return self.strftime("%a, %d %b %Y %H:%M:%S")

    @property
    def rfc3339_string(self):
        """
        Returns the RFC 3339 formatted string representation of the date.

        The RFC 3339 format is a profile of the ISO 8601 standard for representing dates and times.
        This method appends the letter 'Z' to the end of the string to indicate that the time is in UTC.

        Returns:
            str: The RFC 3339 formatted string representation of the date.
        """
        return self.isoformat() + "Z"

    @property
    def local_string(self):
        """
        Returns a string representation of the date and time in the local timezone.

        Returns:
            str: A string representation of the date and time in the local timezone.
        """
        return self.strftime("%c")

    @property
    def human_readable(self):
        """
        Returns a human-readable representation of the date and time.

        Returns:
            str: A string representing the date and time in the format:
                 "{day} de {month} de {year} a las {hour}:{minute}"
        """
        return f"{self.day} de {self._spanish_months[self.month]} de {self.year} a las {str(self.hour).zfill(2)}:{str(self.minute).zfill(2)}"

    def human_readable_date(self):
        """
        Returns a human-readable date string in the format: "{day} de {month} de {year}".
        """
        return f"{self.day} de {self._spanish_months[self.month]} de {self.year}"

    def human_readable_time(self):
        """
        Return a pretty string representation of the time
        in the format HH:MM.

        Returns:
            str: A formatted string representing the time.
        """
        return f"{str(self.hour).zfill(2)}:{str(self.minute).zfill(2)}"

    def add_days(self, days: int):
        """
        Adds the specified number of days to the current date.

        Args:
            days (int): The number of days to add.

        Returns:
            datetime: The resulting date after adding the specified number of days.
        """
        return self + relativedelta(days=days)

    def add_months(self, months: int):
        """
        Adds the specified number of months to the current date.

        Args:
            months (int): The number of months to add.

        Returns:
            datetime: The resulting date after adding the specified number of months.
        """
        return self + relativedelta(months=months)

    def add_years(self, years: int):
        """
        Adds the specified number of years to the current date.

        Args:
            years (int): The number of years to add.

        Returns:
            datetime: The resulting date after adding the specified number of years.
        """
        return self + relativedelta(years=years)

    def add_hours(self, hours: int):
        """
        Adds the specified number of hours to the current date and time.

        Args:
            hours (int): The number of hours to add.

        Returns:
            datetime: The updated date and time after adding the specified hours.
        """
        return self + relativedelta(hours=hours)

    def add_minutes(self, minutes: int):
        """
        Adds the specified number of minutes to the current date and time.

        Args:
            minutes (int): The number of minutes to add.

        Returns:
            datetime: The updated date and time.

        """
        return self + relativedelta(minutes=minutes)

    def add_seconds(self, seconds: int):
        """
        Adds the specified number of seconds to the current date and time.

        Args:
            seconds (int): The number of seconds to add.

        Returns:
            datetime: The updated date and time.

        """
        return self + relativedelta(seconds=seconds)

    @property
    def start_of_year(self):
        """
        Returns a new datetime object representing the very first microsecond of the year. (e.g., 2021-01-01 00:00:00.000000)
        """
        return self.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    @property
    def end_of_year(self):
        """
        Returns a datetime object representing the very last microsecond of the year. (e.g., 2021-12-31 23:59:59.999999)
        """
        return self.replace(
            month=12,
            day=31,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        )

    @property
    def start_of_month(self):
        """
        Returns a new datetime object representing the very first microsecond of the month. (e.g., 2021-02-01 00:00:00.000000)

        This method replaces the day, hour, minute, second, and microsecond
        components of the date with the first day, 00:00:00.000000 of the month.
        """
        return self.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

    @property
    def end_of_month(self):
        """
        Returns the very last microsecond of the month. (e.g., 2021-02-28 23:59:59.999999)

        This method replaces the day, hour, minute, second, and microsecond
        components of the date with the last day, 23:59:59.999999 of the month.
        """
        return self.replace(
            day=1,
            hour=23,
            minute=59,
            second=59,
            microsecond=999999,
        ) + relativedelta(months=1, days=-1)

    @classmethod
    def get_month_spanish_name(cls, month: int) -> str:
        """
        Returns the name of the month in Spanish.

        Args:
            month (int): The month number (1-12).

        Returns:
            str: The name of the month in Spanish.
        """
        return cls._spanish_months[month]

    @classmethod
    def overlaps(cls, start1, end1, start2, end2) -> bool:
        """
        Check if two time intervals overlap.

        Args:
            start1 (datetime): The start time of the first interval.
            end1 (datetime): The end time of the first interval.
            start2 (datetime): The start time of the second interval.
            end2 (datetime): The end time of the second interval.

        Returns:
            bool: True if the intervals overlap, False otherwise.
        """
        if not end1:
            end1 = cls.max
        if not end2:
            end2 = cls.max
        return start1 <= end2 and start2 <= end1

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Returns a pydantic_core.CoreSchema that behaves in the following ways:

        * strings will be parsed as `Date`
        * `Date` instances will be parsed as `Date` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a string
        """

        def validate_from_str(value: str) -> "Date":
            if isinstance(value, datetime):
                return Date(
                    value.year,
                    value.month,
                    value.day,
                    value.hour,
                    value.minute,
                    value.second,
                )
            if isinstance(value, str):
                return Date(value)
            raise ValueError("Invalid date format")

        def serialize(value: Date) -> str:
            return str(value)

        from_str_schema = core_schema.no_info_plain_validator_function(
            validate_from_str
        )

        schema = core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=from_str_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize, when_used="json"
            ),
        )

        return schema

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _: core_schema.CoreSchema,
        schema_handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        json_schema = schema_handler(core_schema.str_schema())
        return json_schema


class EarlyInstanceWarning(Warning):
    pass
