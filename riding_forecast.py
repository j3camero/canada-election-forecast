import csv
import sys

party_long_names = {
    'CON': 'Conservative/Conservateur',
    'LIB': 'Liberal/Lib',
    'NDP': 'NDP-New Democratic Party/NPD-Nouveau Parti d',
    'GRN': 'Green Party/Parti Vert',
    'BQ': 'Bloc Qu',
}

province_to_region = {
    'Newfoundland and Labrador': 'ATL',
    'Prince Edward Island': 'ATL',
    'Nova Scotia': 'ATL',
    'New Brunswick': 'ATL',
    'Quebec': 'QC',
    'Ontario': 'ON',
    'Manitoba': 'SKMB',
    'Saskatchewan': 'SKMB',
    'Alberta': 'AB',
    'British Columbia': 'BC',
    'Yukon': 'TERR',
    'Northwest Territories': 'TERR',
    'Nunavut': 'TERR',
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

def LoadMatrix(filename):
    """Loads a table of numbers from a CSV file.

    The table of numbers should have labeled columns and rows. The first row
    of the CSV file will contain column labels. The first cell in each row
    thereafter will be a label for that row. The first column of the first
    row must be blank. All other cells in the CSV file should contain numbers.

    The returned table is indexed first by column label then by row label.

    Example file format:
    ,ColumnOne,ColumnTwo
    RowOne,1,2
    RowTwo,3,4

    Example usage:
    m = LoadMatrix('example.csv')
    print m['ColumnTwo']['RowOne']
    # Prints 2
    """
    matrix = {}
    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            row_label = row['']
            for column_label, value in row.items():
                if not column_label:
                    continue
                if column_label not in matrix:
                    matrix[column_label] = {}
                try:
                    value = float(value)
                except:
                    # Blank values default to zero.
                    value = 0
                matrix[column_label][row_label] = value
    return matrix

def NormalizeDictVector(d):
    """Adjusts numerical values so they add up to 1."""
    norm = {}
    divisor = sum(d.values())
    for key in d:
        norm[key] = d[key] / divisor
    return norm

# Load regional polling data.
regional_support_before = LoadMatrix('regional_baseline.csv')
regional_poll_averages = LoadMatrix('regional_poll_averages.csv')

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
        before = regional_support_before[region][party]
        after = regional_poll_averages[region][party]
        projected_gain = after / before
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
        if new_riding_number not in new_ridings:
            new_ridings[new_riding_number] = {
                'name': new_riding_name,
                'number': new_riding_number,
                'province': province,
                'feeders': {}}
        r = new_ridings[new_riding_number]
        r['feeders'][old_riding_number] = population_percent
party_order = ['CON', 'NDP', 'LIB', 'GRN', 'BQ']
print 'province,name,number,' + ','.join(p.lower() for p in party_order)
for r in new_ridings.values():
    projections = {}
    for feeder_number, weight in r['feeders'].items():
        feeder = old_ridings[feeder_number]
        norm = NormalizeDictVector(feeder['projections'])
        for party, support in norm.items():
            if party not in projections:
                projections[party] = 0
            projections[party] += support * weight
    ordered_projections = [projections.get(p, 0) for p in party_order]
    row = [r['province'], r['name'], r['number']] + ordered_projections
    print ','.join([str(x) for x in row])
