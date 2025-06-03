## GoogleTrends.py
Pulls [Google Trends](https://trends.google.com/trends/) data using [pytrends](https://github.com/GeneralMills/pytrends) for a given list of keywords and (optional) date range.

Some things worth knowing before you try to read into this class:
- Google Trends has several options for data granularity (hourly, daily, weekly, etc.). The data granularity returned by pytrends depends on the given date range (see below).

| Granularity returned | Time between date range given |
| -------------------- | ----------------------------- |
| Daily                | 1-269 days                    |
| Weekly               | 270 days - 269 weeks          |
| Monthly              | \> 269 weeks                  |
- I didn't include the option to pull hourly data because we don't need it for our use case. But pytrends and Google Trends themselves do have the option to pull hourly data.

## datehandler.py
Class I made to handle all date related calculations for Google Trends. Main purpose is to make sure start and end dates are appropriate. 

For example, all the indices of weekly data fall on a Sunday. So we want to make sure the start date falls on a Sunday & end date falls on a Saturday. Otherwise, we'll have incomplete data for certain weeks, which could be misleading.

More info in the docstrings.