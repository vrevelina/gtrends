from dateutil import parser
import utils

class DateHandler:

    def __init__(self, freq, end_date=None, start_date=None):
        self.freq = freq
        self.end_date = end_date
        self.start_date = start_date

    @property
    def end_date(self):
        return self._end_date
    
    @end_date.setter
    def end_date(self, edate):
        if utils.enddate_is_valid(self.freq, edate):
            self._end_date = parser.parse(edate)
        else:
            self._end_date = utils.get_default_edate(self.freq)
            print(f"Defaulting end date to {self._end_date:%Y-%m-%d}")

    @property
    def start_date(self):
        return self._start_date
    
    @start_date.setter
    def start_date(self, sdate):
        if utils.startdate_is_valid(self.freq, sdate, self._end_date):
            self._start_date = parser.parse(sdate)
        else:
            self._start_date = utils.get_default_sdate(self.freq, self._end_date)
            print(f"Defaulting start date to {self._start_date:%Y-%m-%d}")
    

        

if __name__ == "__main__":
    x = DateHandler("weekly", "2025-05-08", "2025-05-10")
    print("done")
