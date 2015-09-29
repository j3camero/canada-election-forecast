import datetime

from regional_poll_interpolator import RegionalPollInterpolator

interpolator = RegionalPollInterpolator()
interpolator.LoadFromCsv('regional_poll_averages.csv')
dates = ['2015-08-19', '2015-08-20', '2015-08-21', '2015-08-22',
         '2015-08-23', '2015-08-24']
for date_string in dates:
    date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    print date_string, interpolator.Interpolate('QC', 'ndp', date)
print interpolator.GetMostRecent('SK_MB', 'gpc')
