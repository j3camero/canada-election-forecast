import csv
import datetime

class RegionalPollInterpolator(object):
    def __init__(self):
        self.series_by_region_then_party = dict()

    def LoadFromCsv(self, csv_filename):
        with open(csv_filename) as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                date_string = row[0]
                date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
                region = row[1]
                party = row[2]
                value = float(row[3])
                if region not in self.series_by_region_then_party:
                    self.series_by_region_then_party[region] = dict()
                series_by_party = self.series_by_region_then_party[region]
                if party not in series_by_party:
                    series_by_party[party] = []
                series = series_by_party[party]
                series.append((date, value))
                series.sort()

    def Interpolate(self, region, party, date):
        try:
            series = self.series_by_region_then_party[region][party]
        except:
            return 0
        for i in range(len(series) - 1):
            lo = series[i][0]
            hi = series[i + 1][0]
            if date >= lo and date <= hi:
                interval = (hi - lo).total_seconds()
                partial = (date - lo).total_seconds()
                mix = float(partial) / interval
                begin_value = series[i][1]
                end_value = series[i + 1][1]
                return (1 - mix) * begin_value + mix * end_value
        return 0

    def GetMostRecent(self, region, party):
        try:
            return self.series_by_region_then_party[region][party][-1][1]
        except:
            return 0
