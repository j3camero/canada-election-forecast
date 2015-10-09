import csv

party_names = [
    ('Conservative', 'cpc'),
    ('NDP', 'ndp'),
    ('Liberal', 'lpc'),
    ('Bloc', 'bq'),
    ('Green', 'gpc'),
    ('Other', 'oth'),
]

ridings = {}

def AddVotes(riding_number, party_code, additional_votes):
    if riding_number not in ridings:
        ridings[riding_number] = {}
    riding = ridings[riding_number]
    if party_code not in riding:
        riding[party_code] = 0
    riding[party_code] += additional_votes

def NormalizeDictVector(v):
    norm = {}
    divisor = sum(v.values())
    for key, value in v.items():
        norm[key] = float(value) / divisor
    return norm

with open('TRANSPOSITION_338FED.csv', 'rb') as input_file:
    # Skip the first few lines of the file, to get to the data part.
    for i in range(4):
        next(input_file)
    reader = csv.DictReader(input_file)
    for row in reader:
        riding_number = row['2013 FED Number']
        riding_name = row['2013 FED Name']
        for column_header, value in row.items():
            try:
                value = int(value)
            except:
                continue
            for party_name, party_code in party_names:
                if column_header.startswith(party_name):
                    AddVotes(riding_number, party_code, value)
with open('redistributed_2011_results.csv', 'wb') as output_file:
    writer = csv.writer(output_file)
    writer.writerow(['riding', 'date', 'sample_size'] +
                    [p for _, p in party_names])
    for riding_number, vote_counts in ridings.items():
        vote_fractions = NormalizeDictVector(vote_counts)
        ordered_vote_fractions = [vote_fractions[p] for _, p in party_names]
        sample_size = sum(vote_counts.values())
        writer.writerow([riding_number, '2011-05-02', sample_size] +
                        ordered_vote_fractions)
