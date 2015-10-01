import csv
import datetime

from scipy.stats import norm

from regional_poll_interpolator import RegionalPollInterpolator
import riding_poll_model

party_long_names = {
    'cpc': 'Conservative/Conservateur',
    'lpc': 'Liberal/Lib',
    'ndp': 'NDP-New Democratic Party/NPD-Nouveau Parti d',
    'gpc': 'Green Party/Parti Vert',
    'bq': 'Bloc Qu',
    'oth': 'Independent',
}

province_to_region = {
    'Newfoundland and Labrador': 'ATL',
    'Prince Edward Island': 'ATL',
    'Nova Scotia': 'ATL',
    'New Brunswick': 'ATL',
    'Quebec': 'QC',
    'Ontario': 'ON',
    'Manitoba': 'SK_MB',
    'Saskatchewan': 'SK_MB',
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Yukon': 'Canada',
    'Northwest Territories': 'Canada',
    'Nunavut': 'Canada',
}

province_abbreviations = {
    'Newfoundland and Labrador': 'NL',
    'Prince Edward Island': 'PE',
    'Nova Scotia': 'NS',
    'New Brunswick': 'NB',
    'Quebec': 'QC',
    'Ontario': 'ON',
    'Manitoba': 'MB',
    'Saskatchewan': 'SK',
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Yukon': 'YT',
    'Northwest Territories': 'NT',
    'Nunavut': 'NU',
}

provinces_by_numeric_code = {
    '10': 'NL',
    '11': 'PE',
    '12': 'NS',
    '13': 'NB',
    '24': 'QC',
    '35': 'ON',
    '46': 'MB',
    '47': 'SK',
    '48': 'AB',
    '59': 'BC',
    '60': 'YT',
    '61': 'NT',
    '62': 'NU',
}

def WhichParty(s):
    """If the given string contains a party name, return its abbreviation."""
    for abbreviation, long_name in party_long_names.items():
        if long_name in s:
            return abbreviation
    return None

def WhichRegion(s):
    """If the given string contains a province name, return its region code."""
    for province, region in province_to_region.items():
        if province in s:
            return region
    return None

def WhichProvince(s):
    """If the given string contains a province name, return its short form."""
    for province, abbr in province_abbreviations.items():
        if province in s:
            return abbr
    return None

def NormalizeDictVector(d):
    """Adjusts numerical values so they add up to 1."""
    normalized = {}
    divisor = sum(d.values())
    for key in d:
        normalized[key] = d[key] / divisor
    return normalized

def KeyWithHighestValue(d, forbidden_keys=[]):
    """Return the key with the highest value.

    Optionally, a list of forbidden keys can be provided. If so, the function
    will return the key with the next-highest value, but which is not
    forbidden.
    """
    mv = -1
    mk = None
    for k, v in d.items():
        if k in forbidden_keys:
            continue
        if v > mv:
            mk = k
            mv = v
    return mk

# Load regional polling data.
interpolator = RegionalPollInterpolator()
interpolator.LoadFromCsv('regional_poll_averages.csv')
interpolator.LoadFromCsv('regional_baseline.csv')
baseline_date = datetime.datetime(2011, 5, 2)

# Load and process per-riding election results from 2011.
old_ridings = {}
with open('table_tableau12.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        riding_name = row['Electoral District Name/Nom de circonscription']
        riding_number = row['Electoral District Number']
        popular_vote = float(row['Percentage of Votes Obtained'])
        party = WhichParty(row['Candidate/Candidat'])
        if not party:
            continue
        province = WhichProvince(row['Province'])
        region = WhichRegion(row['Province'])
        assert region
        before = interpolator.Interpolate(region, party, baseline_date)
        after = interpolator.GetMostRecent(region, party)
        if before > 2:  # As in 2% not 200%
            projected_gain = after / before
        else:
            projected_gain = 1
        projection = popular_vote * projected_gain
        if not riding_number in old_ridings:
            old_ridings[riding_number] = {
                '2011': {}, 'projections': {},
                'name': riding_name,
                'number': riding_number,
                'province': province}
        r = old_ridings[riding_number]
        r['2011'][party] = popular_vote
        r['projections'][party] = projection

# Calculate the transposition from old ridings (2003) to new ridings (2013).
new_ridings = {}
with open('TRANSPOSITION_338FED.csv') as csv_file:
    # Skip the first few lines of the file, to get to the data part.
    for i in range(4):
        next(csv_file)
    reader = csv.DictReader(csv_file)
    for row in reader:
        new_riding_number = row['2013 FED Number']
        if not new_riding_number:
            continue
        new_riding_name = row['2013 FED Name']
        old_riding_number = row['2003 FED Number from which the 2013 ' +
                                'FED Number is constituted']
        prov_num_code = row['Province and territory numeric code']
        province = provinces_by_numeric_code[prov_num_code]
        assert province
        population_2013 = float(row['2013 FED - Population'])
        population_transferred = float(
            row['Population transferred to 2013 FED'])
        population_percent = population_transferred / population_2013
        all_votes = row['All votes']
        electors = row['Electors on lists']
        if new_riding_number not in new_ridings:
            new_ridings[new_riding_number] = {
                'name': new_riding_name,
                'number': new_riding_number,
                'province': province,
                'feeders': {},
                'total_votes_2011': 0,
                'total_electors_2011': 0,
                'population': int(population_2013)}
        r = new_ridings[new_riding_number]
        r['feeders'][old_riding_number] = population_percent
        r['total_votes_2011'] += int(all_votes)
        r['total_electors_2011'] += int(electors)

# Output final stats for each riding.
party_order = ['cpc', 'ndp', 'lpc', 'gpc', 'bq', 'oth']
readable_party_names = {
    'cpc': 'CON',
    'lpc': 'LIB',
    'ndp': 'NDP',
    'gpc': 'GRN',
    'bq': 'BQ',
    'oth': 'OTH',
}
with open('riding_forecasts.csv', 'wb') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(
        ['province', 'name', 'number,'] +
        [readable_party_names[p].lower() for p in party_order] +
        ['projected_winner', 'strategic_vote', 'confidence', 'turnout_2011'])
    for r in new_ridings.values():
        projections = {}
        riding_name = r['name']
        riding_number = str(r['number'])
        province = r['province']
        # Project this riding by mixing old-riding projections.
        for feeder_number, weight in r['feeders'].items():
            feeder = old_ridings[feeder_number]
            normalized = NormalizeDictVector(feeder['projections'])
            for party, support in normalized.items():
                if party not in projections:
                    projections[party] = 0
                projections[party] += support * weight
        # Upgrade the projections for ridings that have local polling data.
        projections = riding_poll_model.projections_by_riding_number.get(
                          riding_number, projections)
        ordered_projections = [projections.get(p, 0) for p in party_order]
        projected_winner = KeyWithHighestValue(projections)
        runner_up = KeyWithHighestValue(projections, [projected_winner])
        strategic_vote = KeyWithHighestValue(projections, ['cpc'])
        gap = projections[projected_winner] - projections[runner_up]
        projected_winner = readable_party_names[projected_winner]
        strategic_vote = readable_party_names[strategic_vote]
        confidence = norm.cdf(gap / 0.25)
        turnout = float(r['total_votes_2011']) / r['total_electors_2011']
        csv_writer.writerow([province, riding_name, riding_number] +
                            ordered_projections +
                            [projected_winner, strategic_vote, confidence,
                             turnout])
