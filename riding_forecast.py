import csv

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

regional_support_before = LoadMatrix('regional_baseline.csv')
regional_poll_averages = LoadMatrix('regional_poll_averages.csv')
ridings = {}
with open('table_tableau12.csv') as csv_file:
    reader = csv.DictReader(csv_file)
    for row in reader:
        riding_name = row['Electoral District Name/Nom de circonscription']
        riding_number = row['Electoral District Number']
        popular_vote = float(row['Percentage of Votes Obtained'])
        party = WhichParty(row['Candidate/Candidat'])
        if not party:
            continue
        region = WhichRegion(row['Province'])
        assert region
        before = regional_support_before[region][party]
        after = regional_poll_averages[region][party]
        projected_gain = after / before
        projection = popular_vote * projected_gain
        if not riding_number in ridings:
            ridings[riding_number] = {'2011': {}, 'projections': {},
                                      'name': riding_name,
                                      'number': riding_number}
        r = ridings[riding_number]
        r['2011'][party] = popular_vote
        r['projections'][party] = projection
party_order = ['CON', 'NDP', 'LIB', 'GRN', 'BQ']
print 'Riding Number,Riding Name,CON,NDP,LIB,GRN,BQ,CON,NDP,LIB,GRN,BQ'
for r in ridings.values():
    results_2011 = []
    projections = []
    normalized = NormalizeDictVector(r['projections'])
    for party in party_order:
        if party in r['2011']:
            results_2011.append(r['2011'][party])
        else:
            results_2011.append(0)
        if party in normalized:
            projections.append(normalized[party])
        else:
            projections.append(0)
    row = [r['number'], r['name']] + projections + results_2011
    print ','.join([str(x) for x in row])
