import csv
import datetime
import re
import urllib2

from bs4 import BeautifulSoup

from poll import Poll
from regional_poll_interpolator import RegionalPollInterpolator

party_names = {
    'Cons.': 'cpc',
    'NDP': 'ndp',
    'Liberal': 'lpc',
    'BQ': 'bq',
    'Green': 'gpc',
    'Other': 'oth',
}

province_code_to_region = {
    '10': 'ATL',
    '11': 'ATL',
    '12': 'ATL',
    '13': 'ATL',
    '24': 'QC',
    '35': 'ON',
    '46': 'SK_MB',
    '47': 'SK_MB',
    '48': 'AB',
    '59': 'BC',
    '60': 'Canada',
    '61': 'Canada',
    '62': 'Canada',
}

# For quickly dealing with riding names as they appear on Wikipedia. They're
# not necessarily formatted in the exact way that Elections Canada has them.
riding_names_and_numbers = [
    ('Pitt Meadows.*Maple Ridge', '59022'),
    ('Langley.*Aldergrove', '59016'),
    ('South Surrey.*White Rock', '59030'),
    ('West Nova', '12011'),
    ('Courtenay.*Alberni', '59009'),
    ('Mission.*Matsqui.*Fraser Canyon', '59017'),
    ('Hochelaga', '24028'),
    ('M.*gantic.*L.*rable', '24047'),
    ('Manicouagan', '24046'),
    ('Louis-Saint-Laurent', '24045'),
    ('Louis-H.*bert', '24044'),
    ('Longueuil.*Saint-Hubert', '24043'),
    ('L.*vis.*Lotbini.*re', '24042'),
    ('Longueuil.*Charles-LeMoyne', '24041'),
    ('Laval.*Les .*les', '24040'),
    ('Abbotsford', '59001'),
    ('Esquimalt.*Saanich.*Sooke', '59026'),
    ('Montarville', '24049'),
    ('Mirabel', '24048'),
    ('Edmonton Griesbach', '48015'),
    ('New Westminster.*Burnaby', '59019'),
    ('Winnipeg North', '46012'),
    ('Richmond Centre', '59025'),
    ('Lethbridge', '48026'),
    ('Winnipeg South', '46013'),
    ('Madawaska.*Restigouche', '13005'),
    ('Fundy Royal', '13004'),
    ('Moncton.*Riverview.*Dieppe', '13007'),
    ('Miramichi.*Grand Lake', '13006'),
    ('Acadie.*Bathurst', '13001'),
    ('Chatham-Kent.*Leamington', '35017'),
    ('Fredericton', '13003'),
    ('Beaus.*jour', '13002'),
    ('Davenport', '35018'),
    ('Don Valley East', '35019'),
    ('Saint John.*Rothesay', '13009'),
    ('New Brunswick Southwest', '13008'),
    ('Edmonton West', '48020'),
    ('Prince George.*Peace River.*Northern Rockies', '59024'),
    ('Calgary Shepard', '48011'),
    ('Montcalm', '24050'),
    ('Montmagny.*Islet.*Kamouraska.*Rivi.*re-du-Loup', '24051'),
    ('Mount Royal', '24052'),
    ('Notre-Dame-de-Gr.*ce.*Westmount', '24053'),
    ('Outremont', '24054'),
    ('Papineau', '24055'),
    ('Pierrefonds.*Dollard', '24056'),
    ('Pontiac', '24057'),
    ('Portneuf.*Jacques-Cartier', '24058'),
    ('Qu.*bec', '24059'),
    ('Brandon.*Souris', '46001'),
    ('Calgary Midnapore', '48008'),
    ('Cloverdale.*Langley City', '59007'),
    ('Saanich.*Gulf Islands', '59027'),
    ('Victoria', '59041'),
    ('Chilliwack.*Hope', '59006'),
    ('Portage.*Lisgar', '46007'),
    ('Central Okanagan.*Similkameen.*Nicola', '59005'),
    ('Brantford.*Brant', '35013'),
    ('Kildonan.*St. Paul', '46006'),
    ('Kelowna.*Lake Country', '59014'),
    ('Cariboo.*Prince George', '59004'),
    ('Elmwood.*Transcona', '46005'),
    ('Tobique.*Mactaquac', '13010'),
    ('Etobicoke.*Lakeshore', '35028'),
    ('Etobicoke Centre', '35027'),
    ('Essex', '35026'),
    ('Elgin.*Middlesex.*London', '35025'),
    ('Eglinton.*Lawrence', '35024'),
    ('Durham', '35023'),
    ('Dufferin.*Caledon', '35022'),
    ('Don Valley West', '35021'),
    ('Joliette', '24031'),
    ('Brossard.*Saint-Lambert', '24017'),
    ('Lanark.*Frontenac.*Kingston', '35049'),
    ('Lambton.*Kent.*Middlesex', '35048'),
    ('Kitchener Centre', '35045'),
    ('Kingston and the Islands', '35044'),
    ('Kitchener South.*Hespeler', '35047'),
    ('Kitchener.*Conestoga', '35046'),
    ('Kanata.*Carleton', '35041'),
    ('Huron.*Bruce', '35040'),
    ('King.*Vaughan', '35043'),
    ('Kenora', '35042'),
    ('Calgary Signal Hill', '48012'),
    ('Calgary Skyview', '48013'),
    ('Churchill.*Keewatinook Aski', '46003'),
    ('Burnaby North.*Seymour', '59002'),
    ('Calgary Rocky Ridge', '48010'),
    ('Drummond', '24025'),
    ('Dorval.*Lachine.*LaSalle', '24024'),
    ('Gatineau', '24027'),
    ('Gasp.*sie.*Les .*les-de-la-Madeleine', '24026'),
    ('Ch.*teauguay.*Lacolle', '24021'),
    ('Beauport-C.*te-de-Beaupr.*Orl.*ans-Charlevoix', '24020'),
    ('Compton.*Stanstead', '24023'),
    ('Chicoutimi.*Le Fjord', '24022'),
    ('Yukon', '60001'),
    ('Dauphin.*Swan River.*Neepawa', '46004'),
    ('Honor.*-Mercier', '24029'),
    ('Sydney.*Victoria', '12010'),
    ('Edmonton Mill Woods', '48017'),
    ('Hamilton West.*Ancaster.*Dundas', '35038'),
    ('Hastings.*Lennox and Addington', '35039'),
    ('Saint Boniface.*Saint Vital', '46009'),
    ('Provencher', '46008'),
    ('Edmonton Centre', '48014'),
    ('Flamborough.*Glanbrook', '35030'),
    ('Glengarry.*Prescott.*Russell', '35031'),
    ('Guelph', '35032'),
    ('Haldimand.*Norfolk', '35033'),
    ('Haliburton.*Kawartha Lakes.*Brock', '35034'),
    ('Hamilton Centre', '35035'),
    ('Hamilton East.*Stoney Creek', '35036'),
    ('Hamilton Mountain', '35037'),
    ('Etobicoke North', '35029'),
    ('Mississauga Centre', '35058'),
    ('Mississauga East.*Cooksville', '35059'),
    ('Markham.*Unionville', '35056'),
    ('Milton', '35057'),
    ('Markham.*Stouffville', '35054'),
    ('Markham.*Thornhill', '35055'),
    ('London North Centre', '35052'),
    ('London West', '35053'),
    ('Leeds-Grenville-Thousand Islands and Rideau Lakes', '35050'),
    ('London.*Fanshawe', '35051'),
    ('Souris.*Moose Mountain', '47013'),
    ('Saskatoon West', '47012'),
    ('Saskatoon.*University', '47011'),
    ('Saskatoon.*Grasswood', '47010'),
    ('Yorkton.*Melville', '47014'),
    ('Banff.*Airdrie', '48001'),
    ('Bow River', '48003'),
    ('Battle River.*Crowfoot', '48002'),
    ('Calgary Confederation', '48005'),
    ('Calgary Centre', '48004'),
    ('Calgary Heritage', '48007'),
    ('Calgary Forest Lawn', '48006'),
    ('Egmont', '11003'),
    ('LaSalle.*mard.*Verdun', '24037'),
    ('La Prairie', '24034'),
    ('Lac-Saint-Jean', '24035'),
    ('Jonqui.*re', '24032'),
    ('La Pointe-de-.*le', '24033'),
    ('Hull.*Aylmer', '24030'),
    ('Malpeque', '11004'),
    ('Halifax West', '12006'),
    ('Kings.*Hants', '12007'),
    ('Dartmouth.*Cole Harbour', '12004'),
    ('Halifax', '12005'),
    ('Central Nova', '12002'),
    ('Cumberland.*Colchester', '12003'),
    ('Laurentides.*Labelle', '24038'),
    ('Laurier.*Sainte-Marie', '24039'),
    ('York South.*Weston', '35120'),
    ('Humber River.*Black Creek', '35121'),
    ('Vancouver East', '59035'),
    ('Don Valley North', '35020'),
    ('Foothills', '48022'),
    ('Red Deer.*Lacombe', '48030'),
    ('Nickel Belt', '35069'),
    ('Niagara West', '35068'),
    ('St. Albert.*Edmonton', '48031'),
    ('Mississauga.*Streetsville', '35063'),
    ('Mississauga.*Malton', '35062'),
    ('Mississauga.*Lakeshore', '35061'),
    ('Mississauga.*Erin Mills', '35060'),
    ('Niagara Falls', '35067'),
    ('Niagara Centre', '35066'),
    ('Newmarket.*Aurora', '35065'),
    ('Nepean', '35064'),
    ('Sackville.*Preston.*Chezzetcook', '12008'),
    ('Edmonton Riverbend', '48018'),
    ('Edmonton Strathcona', '48019'),
    ('Regina.*Appelle', '47008'),
    ('Regina.*Wascana', '47009'),
    ('Carlton Trail.*Eagle Creek', '47004'),
    ('Moose Jaw.*Lake Centre.*Lanigan', '47005'),
    ('Prince Albert', '47006'),
    ('Regina.*Lewvan', '47007'),
    ('Edmonton Manning', '48016'),
    ('Battlefords.*Lloydminster', '47001'),
    ('Cypress Hills.*Grasslands', '47002'),
    ('Desneth.*Missinippi.*Churchill River', '47003'),
    ('Ahuntsic-Cartierville', '24003'),
    ('Abitibi.*T.*miscamingue', '24002'),
    ('Abitibi.*Baie-James.*Nunavik.*Eeyou', '24001'),
    ('Vancouver South', '59040'),
    ('Beauce', '24007'),
    ('Avignon.*La Mitis.*Matane.*Matap.*dia', '24006'),
    ('Argenteuil.*La Petite-Nation', '24005'),
    ('Alfred-Pellan', '24004'),
    ('B.*cancour.*Nicolet.*Saurel', '24009'),
    ('Beauport.*Limoilou', '24008'),
    ('Brampton North', '35010'),
    ('North Vancouver', '59021'),
    ('Brampton South', '35011'),
    ('Nanaimo.*Ladysmith', '59018'),
    ('York.*Simcoe', '35119'),
    ('York Centre', '35118'),
    ('Windsor West', '35117'),
    ('Cambridge', '35016'),
    ('Willowdale', '35115'),
    ('Whitby', '35114'),
    ('Wellington.*Halton Hills', '35113'),
    ('Waterloo', '35112'),
    ('Vaughan.*Woodbridge', '35111'),
    ('University.*Rosedale', '35110'),
    ('Medicine Hat.*Cardston.*Warner', '48027'),
    ('Lac-Saint-Louis', '24036'),
    ('Lakeland', '48025'),
    ('Grande Prairie.*Mackenzie', '48024'),
    ('Fort McMurray.*Cold Lake', '48023'),
    ('Bruce.*Grey.*Owen Sound', '35014'),
    ('Edmonton.*Wetaskiwin', '48021'),
    ('Charlottetown', '11002'),
    ('Burlington', '35015'),
    ('Cardigan', '11001'),
    ('Red Deer.*Mountain View', '48029'),
    ('Peace River.*Westlock', '48028'),
    ('Sault Ste. Marie', '35092'),
    ('Vancouver Kingsway', '59038'),
    ('Windsor.*Tecumseh', '35116'),
    ('Selkirk.*Interlake.*Eastman', '46010'),
    ('Winnipeg South Centre', '46014'),
    ('Winnipeg Centre', '46011'),
    ('Charleswood.*St. James.*Assiniboia.*Headingley', '46002'),
    ('Rimouski-Neigette.*T.*miscouata.*Les Basques', '24018'),
    ('Charlesbourg.*Haute-Saint-Charles', '24019'),
    ('Pierre-Boucher.*Les Patriotes.*Verch.*res', '24014'),
    ('Bourassa', '24015'),
    ('Brome.*Missisquoi', '24016'),
    ('South Shore.*St. Margarets', '12009'),
    ('Bellechasse.*Les Etchemins.*L.*vis', '24010'),
    ('Beloeil.*Chambly', '24011'),
    ('Berthier.*Maskinong.*', '24012'),
    ('Th.*r.*se-De Blainville', '24013'),
    ('Toronto Centre', '35108'),
    ('Toronto.*Danforth', '35109'),
    ('Calgary Nose Hill', '48009'),
    ('Surrey Centre', '59032'),
    ('Surrey.*Newton', '59033'),
    ('Simcoe North', '35100'),
    ('Spadina.*Fort York', '35101'),
    ('Stormont.*Dundas.*South Glengarry', '35102'),
    ('Sudbury', '35103'),
    ('Thornhill', '35104'),
    ('Thunder Bay.*Rainy River', '35105'),
    ('Thunder Bay.*Superior North', '35106'),
    ('Timmins.*James Bay', '35107'),
    ('Labrador', '10004'),
    ('Long Range Mountains', '10005'),
    ('St. John\'s East', '10006'),
    ('St. John\'s South.*Mount Pearl', '10007'),
    ('Yellowhead', '48034'),
    ('Avalon', '10001'),
    ('Bonavista.*Burin.*Trinity', '10002'),
    ('Coast of Bays.*Central.*Notre Dame', '10003'),
    ('Vancouver Granville', '59036'),
    ('Steveston.*Richmond East', '59031'),
    ('North Island.*Powell River', '59037'),
    ('St. Catharines', '35089'),
    ('Carleton', '35088'),
    ('Vancouver Centre', '59034'),
    ('Burnaby South', '59003'),
    ('Parkdale.*High Park', '35081'),
    ('Oxford', '35080'),
    ('Perth.*Wellington', '35083'),
    ('Cape Breton.*Canso', '12001'),
    ('Pickering.*Uxbridge', '35085'),
    ('Peterborough.*Kawartha', '35084'),
    ('Richmond Hill', '35087'),
    ('Renfrew.*Nipissing.*Pembroke', '35086'),
    ('Saint-L.*onard.*Saint-Michel', '24069'),
    ('Saint-Laurent', '24068'),
    ('Parry Sound.*Muskoka', '35082'),
    ('Nunavut', '62001'),
    ('Richmond.*Arthabaska', '24061'),
    ('Repentigny', '24060'),
    ('Rivi.*re-du-Nord', '24063'),
    ('Rivi.*re-des-Mille-.*les', '24062'),
    ('Marc-Aur.*le-Fortin', '24065'),
    ('Rosemont.*La Petite-Patrie', '24064'),
    ('Saint-Jean', '24067'),
    ('Saint-Hyacinthe.*Bagot', '24066'),
    ('Oshawa', '35074'),
    ('Ottawa Centre', '35075'),
    ('Orl.*ans', '35076'),
    ('Ottawa South', '35077'),
    ('Nipissing.*Timiskaming', '35070'),
    ('Northumberland.*Peterborough South', '35071'),
    ('Oakville', '35072'),
    ('Oakville North.*Burlington', '35073'),
    ('Ottawa.*Vanier', '35078'),
    ('Ottawa West.*Nepean', '35079'),
    ('Northwest Territories', '61001'),
    ('West Vancouver.*Sunshine Coast.*Sea to Sky Country', '59042'),
    ('South Okanagan.*West Kootenay', '59029'),
    ('Sherwood Park.*Fort Saskatchewan', '48032'),
    ('Skeena.*Bulkley Valley', '59028'),
    ('Coquitlam.*Port Coquitlam', '59008'),
    ('North Okanagan.*Shuswap', '59020'),
    ('Scarborough Southwest', '35098'),
    ('Simcoe.*Grey', '35099'),
    ('Fleetwood.*Port Kells', '59012'),
    ('Brampton West', '35012'),
    ('Scarborough.*Agincourt', '35093'),
    ('Toronto.*St.*s', '35090'),
    ('Sarnia.*Lambton', '35091'),
    ('Scarborough North', '35096'),
    ('Scarborough.*Rouge Park', '35097'),
    ('Scarborough Centre', '35094'),
    ('Scarborough.*Guildwood', '35095'),
    ('Cowichan.*Malahat.*Langford', '59010'),
    ('Vimy', '24078'),
    ('Vancouver Quadra', '59039'),
    ('Delta', '59011'),
    ('Shefford', '24072'),
    ('Sherbrooke', '24073'),
    ('Saint-Maurice.*Champlain', '24070'),
    ('Salaberry.*Suro.*t', '24071'),
    ('Trois-Rivi.*res', '24076'),
    ('Ville-Marie.*Le Sud-Ouest.*le-des-Soeurs', '24077'),
    ('Vaudreuil.*Soulanges', '24074'),
    ('Terrebonne', '24075'),
    ('Ajax', '35001'),
    ('Kamloops.*Thompson.*Cariboo', '59013'),
    ('Aurora.*Oak Ridges.*Richmond Hill', '35003'),
    ('Algoma.*Manitoulin.*Kapuskasing', '35002'),
    ('Barrie.*Springwater.*Oro-Medonte', '35005'),
    ('Barrie.*Innisfil', '35004'),
    ('Beaches.*East York', '35007'),
    ('Bay of Quinte', '35006'),
    ('Brampton East', '35009'),
    ('Brampton Centre', '35008'),
    ('Sturgeon River.*Parkland', '48033'),
    ('Port Moody.*Coquitlam', '59023'),
    ('Kootenay.*Columbia', '59015'),
]

def RidingNameToNumber(riding_name):
    for name_pattern, number in riding_names_and_numbers:
        if re.match(name_pattern, riding_name):
            return number
    return None

def RidingNumberToRegionCode(riding_number):
    province_code = str(riding_number)[0:2]
    return province_code_to_region[province_code]

def DictVectorToString(vector):
    strings = []
    for k, v in sorted(vector.items()):
        strings.append('%s %.2f' % (k, v))
    return ' '.join(strings)

def FindColumnHeaders(header_row):
    party_columns = {n: -1 for n in party_names}
    date_column = -1
    sample_size_column = -1
    for column_index, column_title in enumerate(header_row.find_all('th')):
        column_title = column_title.get_text().replace('\n', ' ')
        if column_title == 'Last Date of Polling':
            date_column = column_index
        if column_title.startswith('Sample Size'):
            sample_size_column = column_index
        if column_title in party_columns:
            party_columns[column_title] = column_index
    assert date_column >= 0
    assert sample_size_column >= 0
    return date_column, sample_size_column, party_columns

def ExtractPollsFromTable(table, riding_number, riding_name):
    polls = []
    rows = table.find_all('tr')
    date_column, sample_size_column, party_columns = FindColumnHeaders(rows[0])
    for row in rows[1:]:
        columns = row.find_all('td')
        date_string = columns[date_column].find('span', '').get_text()
        parsed_date = datetime.datetime.strptime(date_string, '%B %d, %Y')
        age_seconds = (datetime.datetime.now() - parsed_date).total_seconds()
        age_days = float(age_seconds) / 86400
        if age_days > 21:
            continue
        sample_size_string = columns[sample_size_column].get_text().strip()
        if sample_size_string:
            sample_size = float(sample_size_string.replace(',', ''))
        else:
            sample_size = 0
        poll = Poll(parsed_date, sample_size, riding_number, riding_name)
        for party_name, party_index in party_columns.items():
            if party_index >= 0:
                number_string = columns[party_index].get_text()
                support = float(number_string) / 100
                party_code = party_names[party_name]
                poll.party_support[party_code] = support
        polls.append(poll)
    return polls

def FetchRidingPollsFromWikipedia():
    ridings = {}
    url = ('https://en.wikipedia.org/wiki/Opinion_polling_in_the_Canadian_' +
           'federal_election,_2015_by_constituency')
    response = urllib2.urlopen(url)
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table', 'wikitable sortable')
    riding_titles = soup.find_all('h4')
    assert len(riding_titles) == len(tables)
    ridings_with_local_poll_data = 0
    poll_counter = 0
    for riding_title, table in zip(riding_titles, tables):
        riding_name = riding_title.find('a').get_text()
        riding_number = RidingNameToNumber(riding_name)
        assert riding_number, 'No mapping for riding ' + riding_name
        ridings[riding_number] = ExtractPollsFromTable(table, riding_number,
                                                       riding_name)
    return ridings

# Load the poll data interpolator.
interpolator = RegionalPollInterpolator()
interpolator.LoadFromCsv('regional_poll_averages.csv')
interpolator.LoadFromCsv('regional_baseline.csv')

# The projections based on riding polls are stored in here, keyed by riding
# number as a string.
projections_by_riding_number = {}

raw_polls_by_riding = FetchRidingPollsFromWikipedia()
poll_count = 0
with open('riding_polls.csv', 'w') as csv_file:
    csv_writer = csv.writer(csv_file)
    party_order = ['cpc', 'ndp', 'lpc', 'gpc', 'bq', 'oth']
    for riding_number, raw_polls in raw_polls_by_riding.items():
        region = RidingNumberToRegionCode(riding_number)
        total_weight = sum(p.CalculateRawWeight() for p in raw_polls)
        weighted = {}
        if len(raw_polls) == 0 or total_weight == 0:
            continue
        csv_writer.writerow(['Riding:', riding_number, '', 'Raw Polls',
                             '', '', '', '', '', 'After Swing'])
        csv_writer.writerow(['Date', 'Sample Size', 'Weight'] +
                            party_order + party_order)
        for raw_poll in raw_polls:
            projected = interpolator.ProportionalSwingProjection(region,
                                                                 raw_poll)
            weight = raw_poll.CalculateRawWeight() / total_weight
            raw_ordered = [raw_poll.party_support.get(p, 0)
                           for p in party_order]
            proj_ordered = [projected.party_support.get(p, 0)
                            for p in party_order]
            csv_writer.writerow([raw_poll.date.strftime('%Y-%m-%d'),
                                 raw_poll.sample_size, weight] +
                                raw_ordered + proj_ordered)
            for party, support in projected.party_support.items():
                if party not in weighted:
                    weighted[party] = 0
                weighted[party] += support * weight
            poll_count += 1
        weighted_ordered = [weighted.get(p, 0) for p in party_order]
        csv_writer.writerow(['Weighted', '-', '1'] + weighted_ordered)
        csv_writer.writerow([])
        projections_by_riding_number[riding_number] = weighted
print 'ridings with local poll data:', len(projections_by_riding_number)
print 'total num polls:', poll_count
