from pytrends.request import TrendReq
from datetime import datetime
import pandas as pd
from GoogleTrends import utils
from GoogleTrends.datehandler import datehandler


class GoogleTrends:
    """Class to pull Google Trends data"""

    def __init__(
        self,
        client_name,
        keywords,
        end_date=None,
        start_date=None,
        freq="weekly",
        region="US",
    ):

        self.client_name = client_name
        self.kw_list = keywords
        self.frequency = freq
        self.input_end_date = end_date
        self.input_start_date = start_date
        self.datehandler = datehandler(freq, end_date, start_date)
        self.geo = region
        self.scaled = False

    def _fetch(self, timeframe: str) -> pd.DataFrame:
        """Fetches data for the given timeframe

        Args:
            timeframe (str): timeframe (format= f"{start_date:%Y-%m-%d} {end_date:%Y-%m-%d}")

        Returns:
            pd.DataFrame: Raw data from Google Trends
        """
        gtrends = TrendReq()
        gtrends.build_payload(timeframe=timeframe, kw_list=self.kw_list, geo=self.geo)
        return gtrends.interest_over_time().drop("isPartial", axis=1)

    def get_unscaled_data(
        self, start_date: datetime, end_date: datetime
    ) -> pd.DataFrame:
        """Fetches unscaled data between the given start & end dates

        Args:
            start_date (datetime): start date of data to fetch
            end_date (datetime): end date of data to fetch

        Returns:
            pd.DataFrame: Raw data from Google Trends
        """
        tf = utils.to_timeframe(start_date, end_date)
        return self._fetch(tf)

    def get_df_list(self):
        """Gets a list of dataframes and list of overlapping dates

        If we'd like to fetch data with more granularity for a larger date range, say more than 7 days of daily data,
        we'll have to make several requests in 7 day blocks from the start date to the end date.
        This method will make those repeated requests in cases of date ranges that are larger than the allowed range for daily/weekly data.

        Returns:
            df_list (List): List of pandas dataframes that we would merge later
            op_date_list (List): List of overlapping dates
        """
        current_start = self.datehandler.end_date
        current_end = self.datehandler.end_date
        df_list = []
        op_date_list = []

        while not utils.less_than_gt_range(
            self.datehandler.start_date, current_end, self.frequency
        ):  # while the date range is more than the allowed range
            current_start = utils.get_start_date(current_start, self.frequency)
            df = self.get_unscaled_data(current_start, current_end)
            op_date = utils.get_overlapping_date(df, self.kw_list)
            op_date_list.append(op_date)
            df_list.append(df)
            current_end = op_date
            current_start = current_end

        if (
            utils.less_than_270d(self.datehandler.start_date, current_end)
            and self.frequency == "weekly"
        ):
            raw = self.get_unscaled_for(self.datehandler.start_date, current_end)
            df = self.get_avg(raw)
        else:
            df = self.get_unscaled_for(self.datehandler.start_date, current_end)
        print(f"{self.datehandler.start_date:%Y-%m-%d} {current_end:%Y-%m-%d}")
        df_list.append(df)
        return df_list, op_date_list

    def _scale(self, upper_df: pd.DataFrame, lower_df: pd.DataFrame, op_date):
        min_date_upper = upper_df.index.min()
        op_upper_df = upper_df.loc[:op_date, :]
        op_lower_df = lower_df.loc[min_date_upper:, :]
        numerators = {k: op_upper_df.loc[:, k].sum() for k in self.kw_list}
        denominators = {k: op_lower_df.loc[:, k].sum() for k in self.kw_list}
        for k in self.kw_list:
            scale = numerators[k] / denominators[k]
            lower_df[k] = lower_df[k].apply(lambda x: x * scale)
        lower_df.drop(op_lower_df.index, inplace=True)
        return upper_df.append(lower_df).sort_index()

    def normalize_to_100(self, df: pd.DataFrame):
        """Makes sure the final scaled dataframe's max value is 100

        Args:
            df (pd.DataFrame): scaled dataframe

        Returns:
            pd.DataFrame: final dataframe, normalized so that the max value is 100
        """
        max_val = df.max().max()
        return df.apply(lambda x: x / max_val * 100)

    def get_scaled_data(self):
        self.scaled = True
        df_list, op_date_list = self.get_df_list()
        df = self._scale(df_list[0], df_list[1], op_date_list[0])
        if len(df_list) > 2:
            for i in range(2, len(df_list)):
                df = self._scale(df, df_list[i], op_date_list[i - 1])
        return self.normalize_to_100(df)

    def get_avg(self, df):
        """Gets the avg values of the Google Trends data.

        This is used in the case when we'd like less granularity than what is given by the Google Trends API.
        e.g. Weekly data for a date range < 270 days

        Args:
            df (pd.DataFrame): Raw data from Google Trends.

        Returns:
            pd.DataFrame: Data averaged to the desired granularity.
        """
        idx_name = df.index.name
        df.reset_index(inplace=True)
        if self.frequency == "weekly":
            df["gt_date"] = df[idx_name].apply(utils.get_week_start)
        elif self.frequency == "monthly":
            df["gt_date"] = df[idx_name].apply(utils.first_of_month)
        df.drop(idx_name, axis=1, inplace=True)
        return df.groupby(["gt_date"]).mean()

    def get_dailydata(self):
        if utils.less_than_270d(self.datehandler.start_date, self.datehandler.end_date):
            df = self.get_unscaled_data(
                self.datehandler.start_date, self.datehandler.end_date
            )
        else:
            df = self.get_scaled_data()
        return df

    def get_weeklydata(self):
        if utils.less_than_270d(self.datehandler.start_date, self.datehandler.end_date):
            df = self.get_unscaled_for(
                self.datehandler.start_date, self.datehandler.end_date
            )
            return self.get_avg(df)
        elif utils.less_than_270w(
            self.datehandler.start_date, self.datehandler.end_date
        ):
            return self.get_unscaled_data(
                self.datehandler.start_date, self.datehandler.end_date
            )
        else:
            return self.get_scaled_data()

    def get_monthlydata(self):
        df = self.get_unscaled_data(
            self.datehandler.start_date, self.datehandler.end_date
        )
        if utils.less_than_270w(self.datehandler.start_date, self.datehandler.end_date):
            return self.get_avg(df)
        else:
            return df

    def get_data(self):
        print(
            f"Getting Google Trends Data...\nFrequency: {self.frequency}\nKeywords: {self.kw_list}\nDate Range: {self.datehandler.start_date} - {self.datehandler.end_date}"
        )
        if self.frequency == "daily":
            return self.get_dailydata()
        elif self.frequency == "weekly":
            return self.get_weeklydata()
        elif self.frequency == "monthly":
            return self.get_monthlydata()

    def add_details_to_df(self, raw_data):
        rawd = raw_data.reset_index().rename(columns={"gt_date": "date"})
        df = pd.melt(
            rawd, id_vars=["date"], value_vars=self.kw_list, var_name="keyword"
        )
        new_cols_dict = {
            "client": self.client_name,
            "region": self.geo,
            "scaled": self.scaled,
            "start_date": f"{self.datehandler.start_date:%Y-%m-%d}",
            "input_start_date": self.datehandler.start_date_str,
            "end_date": f"{self.datehandler.end_date:%Y-%m-%d}",
            "input_end_date": self.datehandler.end_date_str,
            "pull_timestamp": utils.get_current_timestamp(),
            "keywords_queried": str(self.kw_list),
        }
        for colname, value in new_cols_dict.items():
            df[colname] = value
        return df

    def get_final_data(self):
        raw_data = self.get_data().apply(round).astype("int")
        return self.add_details_to_df(raw_data)

    def get_fname(self):
        scaled = "scaled" if self.scaled else "raw"
        return f"{datetime.now():%Y%m%d_%H%M%S}_GoogleTrends_{self.client_name}_{self.frequency}_{scaled}_{self.datehandler.start_date:%m%d%y}_{self.datehandler.end_date:%m%d%y}.csv"
