from datetime import datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta, SA, SU
import math
import pandas as pd
from pytrends.request import TrendReq


def is_first_of_month(d):
    return d.day == 1

def is_last_of_month(d):
    next_day = d + relativedelta(days=1)
    return d.month < next_day.month

def is_saturday(d):
    return d.isoweekday() == 6

def is_sunday(d):
    return d.isoweekday() == 7

DELTAS = {
    "daily": {
        "end_date": {
            "is_valid": lambda x: True,
            "delta": relativedelta(days=-1)
        },
        "start_date": {
            "is_valid": lambda x: True,
            "delta": relativedelta(years=-1)
        }
    },
    "weekly": {
        "end_date": {
            "is_valid": is_saturday,
            "delta": relativedelta(days=-1, weekday=SA(-1))
        },
        "start_date": {
            "is_valid": is_sunday,
            "delta": relativedelta(weekday=SU(-52))
    }
    },
    "monthly": {
        "end_date": {
            "is_valid": is_last_of_month,
            "delta": relativedelta(day=1, days=-1)
        },
        "start_date": {
            "is_valid": is_first_of_month,
            "delta": relativedelta(years=-1, day=1)
        }
    },
}

def get_default_edate(freq):
    today = datetime.today()
    return today + DELTAS[freq]["end_date"]["delta"]

def get_default_sdate(freq, edate):
    return edate + DELTAS[freq]["start_date"]["delta"]

def enddate_is_valid(freq, dte):
    try:
        parsed_edate = parser.parse(dte)
        assert DELTAS[freq]["end_date"]["is_valid"](parsed_edate)
        return True
    except parser.ParserError as e:
        print(f"Invalid end date: {e.args[1]}")
    except AssertionError:
        print("End date has to fall on a Saturday for weekly frequency, last of month for monthly")
    except TypeError:
        pass
    return False

def startdate_is_valid(freq, sdate, parsed_edate):
    try:
        parsed_sdate = parser.parse(sdate)
        assert parsed_sdate < parsed_edate
        assert DELTAS[freq]["start_date"]['is_valid'](parsed_sdate)
        return True
    except parser.ParserError as e:
        print(f"Invalid start date: {e.args[1]}")
    except AssertionError:
        print(f"Start date needs to be earlier than the end date ({parsed_edate:%Y-%m-%d}) and fall on a Sunday for weekly frequency, first of month for monthly")
    except TypeError:
        pass
    return False

def to_timeframe(end_date: datetime, start_date: datetime) -> str:
    return f"{start_date:%Y-%m-%d} {end_date:%Y-%m-%d}"

def exceeds_gt_range(end_date, start_date, freq):
    if freq == "daily":
        return (end_date - start_date) > timedelta(days=270)
    elif freq == "weekly":
        return (end_date - start_date) > timedelta(weeks=270)
    
def get_next_end_date(df):
    new_start_date = df[df != 0].idxmin().max()
    min_idx = df.index.get_loc(new_start_date)
    perc_25 = math.ceil(df.shape[0] / 4)
    return df.index[max(min_idx, perc_25)]
