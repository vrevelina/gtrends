## GoogleTrends.py
Pulls [Google Trends](https://trends.google.com/trends/) data using [pytrends](https://github.com/GeneralMills/pytrends) for a given list of keywords and date range.

Google Trends has several options for data granularity (hourly, daily, weekly, etc.). The data granularity returned by pytrends depends on the given date range

| Granularity returned | Time between date range given |
| -------------------- | ----------------------------- |
| Daily                | 1-269 days                    |
| Weekly               | 270 days - 269 weeks          |
| Monthly              | \> 269 weeks                  |

## datehandler.py
Custom class to handle all date related calculations for Google Trends. Main purpose is to make sure start and end dates are appropriate. 

For example, all the indices of weekly data fall on a Sunday. So we want to make sure the start date falls on a Sunday & end date falls on a Saturday. Otherwise, we'll have incomplete data for certain weeks, which could be misleading.
