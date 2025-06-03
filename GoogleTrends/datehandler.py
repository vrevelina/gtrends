import calendar
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, SA, SU
from GoogleTrends import utils


class datehandler:
    def __init__(self, freq, end_date=None, start_date=None):
        """Handles all date related calculations for GoogleTrends

        Args:
            freq (str): granularity
            end_date (str, optional): end date (format: %Y-%m-%d). Defaults to None.
            start_date (str, optional): start date (format: %Y-%m-%d). Defaults to None.
        """
        self.freq = freq
        self.end_date_str = end_date
        self.start_date_str = start_date
        self.end_date = None
        self.start_date = None
        self.set_end_date()
        self.set_start_date()

    def _default_end(self):
        """Returns the default end date based on the given granularity:
        - Daily: Yesterday
        - Weekly: The latest Saturday
        - Monthly: The end of last month

        Returns:
            datetime: default end date.
        """
        yesterday = datetime.today() - timedelta(days=1)
        if self.freq == "daily":
            return yesterday
        elif self.freq == "weekly":
            return yesterday - relativedelta(weekday=SA(-1))
        elif self.freq == "monthly":
            first_of_month = datetime.today().replace(day=1)
            return first_of_month - relativedelta(days=1)

    def _default_start(self):
        """Returns the default start date (1 year before end date) based on the given granularity.
        I put an if statement here because I'd like to make sure that each data point contains the same amount of data.
        e.g.
        (1) If it's weekly, we'd want the start date to fall on a sunday.
        (2) If it's monthly, we'd want the start date to fall on the first of month.

        Returns:
            datetime: default start date.
        """
        if self.freq == "daily":
            return self.end_date - relativedelta(years=1)
        elif self.freq == "weekly":
            return self.end_date - relativedelta(weeks=52, days=-1)
        elif self.freq == "monthly":
            return self.end_date - relativedelta(months=12, day=1)

    def _handle_end(self):
        """Determines the appropriate end date if end date is not None.

        - If it's weekly, we want to make sure the end date falls on a Saturday.
            - Preferably the next saturday after the given end date.
            - Latest saturday if the above isn't possible.
        - If it's monthly, we want to make sure the end date falls at the end of the month.
            - Preferably the end of month of the given date.
            - End of latest month if the above isn't possible.

        """
        yesterday = datetime.today() - timedelta(days=1)
        if self.freq == "weekly":
            next_sat_from_edate = self.end_date + relativedelta(weekday=SA(1))
            if next_sat_from_edate > yesterday:
                self.end_date = self.end_date - relativedelta(weekday=SA(-1))
            else:
                self.end_date = next_sat_from_edate
        elif self.freq == "monthly":
            last_day = calendar.monthrange(self.end_date.year, self.end_date.month)[1]
            last_of_month = self.end_date.replace(day=last_day)
            if last_of_month > yesterday:
                first_of_month = self.end_date.replace(day=1)
                self.end_date = first_of_month - relativedelta(days=1)
            else:
                self.end_date = last_of_month

    def _handle_start(self):
        """Determines the appropriate start date if start date is not None.

        - If it's weekly, we want to make sure the start date falls on a Sunday.
        - If it's monthly, we want to make sure the start date falls on the first of the month.

        """
        if self.freq == "weekly":
            self.start_date = self.start_date - relativedelta(weekday=SU(-1))
        elif self.freq == "monthly":
            self.start_date = self.start_date.replace(day=1)

    def set_end_date(self):
        if self.end_date_str is None:
            self.end_date = self._default_end()
        else:
            self.end_date = utils.to_dt(self.end_date_str)
        self._handle_end()

    def set_start_date(self):
        if self.start_date_str is None:
            self.start_date = self._default_start()
        else:
            self.start_date = utils.to_dt(self.start_date_str)
        self._handle_start()
