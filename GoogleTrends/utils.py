from datetime import datetime, timedelta
import pandas as pd
import math


def to_dt(d: str) -> datetime:
    return datetime.strptime(d, "%Y-%m-%d")


def to_timeframe(start_date: datetime, end_date: datetime) -> str:
    return f"{start_date:%Y-%m-%d} {end_date:%Y-%m-%d}"


def less_than_270d(start_date: datetime, end_date: datetime) -> bool:
    return (end_date - start_date) < timedelta(days=270)


def less_than_270w(start_date: datetime, end_date: datetime) -> bool:
    return (end_date - start_date) < timedelta(weeks=270)


def less_than_gt_range(start_date: datetime, end_date: datetime, freq: str) -> bool:
    if freq == "daily":
        return less_than_270d(start_date, end_date)
    elif freq == "weekly":
        return less_than_270w(start_date, end_date)


def get_week_start(d):
    return d - timedelta(days=d.isoweekday() % 7)


def get_daily_start_date(end_date: datetime) -> datetime:
    return end_date - timedelta(days=269)


def get_weekly_start_date(end_date: datetime) -> datetime:
    return end_date - timedelta(weeks=269)


def get_start_date(end_date: datetime, freq: str) -> datetime:
    if freq == "daily":
        return get_daily_start_date(end_date)
    elif freq == "weekly":
        return get_weekly_start_date(end_date)


def get_overlapping_date(df: pd.DataFrame, kw_list: list) -> pd.Timestamp:
    """Returns a list of overlapping dates.

    Given a dataframe, this function would get a list of the minimum dates of non-zero values for each of the keyword (saved to min_dates)
    Then it would get:
    (1) The maximum date in min_dates (max_date_idx)
    (2) The 25th percentile of the date indices (df_shape25)
    It would then, get the maximum of the two indices, and returns the date at the chosen index.

    The purpose of this function is to scale several dataframes.
    We want to have enough data to use as the scale, but in the case when the top 25% of the data are all 0s, this way of scaling would be useless.
    So we want to make sure that the sum of the values we're using to scale the data isn't 0.
    Hence, the reason why we're getting (1).

    Args:
        df (pd.DataFrame): dataframe
        kw_list (list): list of keywords in the dataframe

    Returns:
        pd.Timestamp: the date/index we'll use to slice the dataframe for scaling.
    """
    min_dates = []
    for k in kw_list:
        s = df.loc[:, k]
        min_dates.append((s[s != 0].index).min())
    max_date_idx = df.index.get_loc(max(min_dates))
    df_shape25 = math.ceil(df.shape[0] / 4)
    return df.index[max(max_date_idx, df_shape25)]


def first_of_month(d: datetime):
    return d.replace(day=1)


def get_current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
