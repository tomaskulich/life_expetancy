import re
from sklearn import linear_model
import math
# from sklearn import svm
# from sklearn.preprocessing import PolynomialFeatures

# https://en.wikipedia.org/wiki/List_of_countries_by_body_mass_index
def parse_obesity():
    f = open('inp_obesity.txt')
    ind = 2
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.replace('| align=left| ','')
        line = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line)
        line = [elem.strip() for elem in tuple(line.split('||'))]
        if line[ind] != '':
            res[line[0]] = float(line[ind])
    return res

# https://en.wikipedia.org/wiki/List_of_countries_by_body_mass_index
def parse_bmi():
    f = open('inp_bmi.txt')
    ind = 2
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.replace('| align=left| ','')
        line = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line)
        line = [elem.strip() for elem in tuple(line.split('||'))]
        if line[ind] not in ['', '-']:
            res[line[0]] = float(line[ind])
    return res

def parse_life_expectancy():
    f = open('inp_life_expectancy.txt')
    ind = 2
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.replace('| align=left| ','')
        line = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line)
        line = tuple(line.split(' || '))
        res[line[0]] = float(line[ind])
    return res

def parse_spending():
    f = open('inp_spending.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.replace('| style="text-align:left" |', '')
        line = tuple(line.split('||'))
        country = re.sub(r' \[\[(.*?)\]\] ', r'\1', line[0])
        money = line[3]
        money = None if money == '' else float(money.replace(',', ''))
        if money != None:
          res[country] = money
    return res

def parse_alcohol():
    f = open('inp_alcohol.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip().split()
        i = 0
        while True:
            try:
                float(line[i])
                break
            except ValueError:
                i += 1
        res[' '.join(line[0:i])] = float(line[i])
    return res

# https://en.wikipedia.org/wiki/List_of_countries_by_cigarette_consumption_per_capita
def parse_cigarettes():
    f = open('inp_cigarettes.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.split('||')
        country = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line[1].strip()).strip()
        cigarettes = float(line[2].strip())
        res[country] = cigarettes
    return res

def parse_traffic():
    f = open('inp_traffic.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        if line.startswith('||'):
            line = line[2:]
        line = line.split('||')
        country = re.sub(r'\| \{\{[a-z]*\|(.*?)\}\}', r'\1', line[0].strip())
        traffic_str = line[1].strip()
        if traffic_str == '-':
            # Monaco does not report traffic accidents
            traffic = 0
        else:
            traffic = float(traffic_str)
        res[country] = traffic
    return res

def parse_gdp():
    f = open('inp_gdp.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip().split()
        i = 0
        while True:
            try:
                float(line[i])
                break
            except ValueError:
                i += 1
        res[' '.join(line[0:i])] = float(line[i])
    return res

aliases = [
  ['Russian Federation', 'Russia'],
  ['Slovak Republic', 'Slovakia'],
  ['Venezuela', 'Venezuela, RB'],
  ['United Republic of Tanzania', 'Tanzania'],
  ['Iran', 'Iran, Islamic Rep.'],
  ['United States of America', 'United States'],
  ['Laos', 'Lao PDR', 'Lao People\'s Democratic Republic'],
  ['Brunei', 'Brunei Darussalam'],
  ['Syria', 'Syrian Arab Republic'],
  ['Cape Verde', 'Cabo Verde'],
  ['Republic of Korea', 'Korea, Rep.'],
  ['Micronesia', 'Micronesia, Fed. Sts.', 'Federated States of Micronesia'],
  ['Vietnam', 'Viet Nam'],
  ['Moldova', 'Republic of Moldova'],
  ['Macedonia', 'Macedonia|Republic of Macedonia', 'Republic of Macedonia|Macedonia'],
  ['Congo, Dem. Rep.', 'Democratic Republic of the Congo'],
  ['Ivory Coast', 'Cote d\'Ivoire'],
  ['Egypt', 'Egypt, Arab Rep.'],
  ['Bahamas', 'Bahamas, The'],
]

values = {} # {feature_name: {country_name: value}}
values['life_expectancy'] = parse_life_expectancy()
values['obesity'] = parse_obesity()
values['bmi'] = parse_bmi()
values['spending'] = parse_spending()
values['alcohol'] = parse_alcohol()
values['cigarettes'] = parse_cigarettes()
values['traffic'] = parse_traffic()
values['gdp'] = parse_gdp()

def make_normalized():
    for i, _ in enumerate(features_x):
        data = [record[i] for record in x] + [record[i] for record in px]
        mean = sum(data)/len(data)
        sigma = math.sqrt(sum((v - mean) ** 2 for v in data) / len(data))
        for record in x + px:
            record[i] = (record[i] - mean) / sigma

def expand():
    to_append = []
    for i, feature_name in enumerate(features_x):
        if feature_name == 'spending':
            to_append.append('log_spending')
            for record in x + px:
                record.append(math.log(record[i]))
        #for deg in range(2, 3):
        #    for record in x + px:
        #        record.append(record[i] ** deg)
        #    to_append.append('%s_pow_%d'%(feature_name, deg))
    features_x.extend(to_append)

def get_value(values, country, values_name = None):
    result = []
    if country in values:
        result.append(values[country])
    for alias in aliases:
        for alias1 in alias:
            for alias2 in alias:
                if alias1 != alias2:
                    if alias1 == country and alias2 in values:
                        result.append(values[alias2])
    if len(result) == 0:
        return None
    if len(result) > 1:
        raise Exception('country %s present multiple times in %s' % (country, values_name))
    return result[0]

def country_equal(country1, country2):
    if country1 == country2:
        return True
    for alias in aliases:
        for alias1 in alias:
            for alias2 in alias:
                if alias1 != alias2 and alias1 == country1 and alias2 == country2:
                    return True
    return False


country_tbp = 'Slovak Republic'
#country_tbp = 'Switzerland'
#country_tbp = 'Vietnam'

features_x = ['spending', 'cigarettes', 'alcohol', 'traffic', 'gdp', 'bmi', 'obesity']
#features_x = ['cigarettes', 'alcohol', 'traffic']
feature_tbp = 'life_expectancy'
all_features = features_x + [feature_tbp]

not_have = set()
for country in values['life_expectancy']:
    for values_names in all_features:
        if get_value(values[values_names], country) == None:
            not_have.add(country)

countries = list(set(values['life_expectancy'].keys()) - not_have)

x = []
y = []
for country in countries:
    if country_equal(country, country_tbp):
        continue
    xx = []
    for values_names in features_x:
        xx.append(get_value(values[values_names], country))
    x.append(xx)
    y.append(get_value(values[feature_tbp], country))

px = []
for values_names in features_x:
    px.append(get_value(values[values_names], country_tbp))


px = [px]

expand()
make_normalized()

#print(x, px, features_x)

#clf = svm.SVR(kernel = 'poly', degree = 1, C=1e4)
#poly = PolynomialFeatures(degree=2)
#x = poly.fit_transform(x)
#px = poly.fit_transform(px)

#clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1)
clf = linear_model.LinearRegression()
print('countries: %d'%len(countries))
print(clf.fit(x, y))
print('score: %f'%clf.score(x,y))
coef = {feature: clf.coef_[i] for i, feature in enumerate(features_x)}
print(coef, clf.intercept_)

predict = clf.predict(px)

print(predict, get_value(values[feature_tbp], country_tbp))
