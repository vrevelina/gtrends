from pytrends.request import TrendReq
from datetime import datetime, timedelta
import pandas as pd
from datehandler import DateHandler
import utils

class GoogleTrends:
    def __init__(self,
                 keywords,
                 end_date=None,
                 start_date=None,
                 frequency="weekly",
                 region="US"):
        self.kw_list = keywords
        self.freq = frequency
        self.dhandler = DateHandler(freq=frequency, end_date=end_date, start_date=start_date)
        self.geo = region
        self.scaled = False

    def get_raw_data(self, end_date, start_date) -> pd.DataFrame:
        """Fetches data for the given timeframe

        Args:
            timeframe (str): timeframe (format= f"{start_date:%Y-%m-%d} {end_date:%Y-%m-%d}")

        Returns:
            pd.DataFrame: Raw data from Google Trends
        """
        tf = utils.to_timeframe(end_date, start_date)
        gtrends = TrendReq()
        gtrends.build_payload(timeframe=tf, kw_list=self.kw_list, geo=self.geo)
        return gtrends.interest_over_time().drop("isPartial", axis=1)

    def get_scaled_data(self) -> pd.DataFrame:
        self.scaled = True
        delta = timedelta(days=269) if self.freq == "daily" else timedelta(weeks=269)
        current_end = self.dhandler.end_date
        current_start = self.dhandler.end_date - delta
        while current_start > self.dhandler.start_date:
            df = self.get_raw_data(current_end, current_start)
            current_end = utils.get_next_end_date(df)