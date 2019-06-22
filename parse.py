import re
import math
from sklearn import svm
from sklearn import linear_model
from sklearn import isotonic
from sklearn.preprocessing import PolynomialFeatures

# {{{ parse all
def parse_household():
    f = open('inp_household.txt')
    ind = 2
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        line = line.replace(' align="left" | ','')
        if line == '|-' or line == '|}':
            continue
        line = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line)
        line = tuple(line.split('||'))
        res[line[1].strip()] = float(line[ind].replace(',', '').strip())
    return res

def parse_cars():
    f = open('inp_cars.txt')
    ind = 2
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = re.sub(r'\{\{flag\|(.*?)\}\}', r'\1', line)
        line = tuple(line.split('||'))
        res[line[1].strip()] = float(line[ind].replace(',', '').strip())
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

def parse_ppp():
    f = open('inp_ppp.txt')
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


def parse_cigarettes():
    f = open('inp_cigarettes.txt')
    lines = f.readlines()
    res = {}
    for line in lines:
        line = line.strip()
        if line == '|-' or line == '|}':
            continue
        line = line.split('||')
        country = re.sub(r'\{\{flagcountry\|(.*?)\}\}', r'\1', line[1].strip()).strip()
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

values = {}
values['life_expectancy'] = parse_life_expectancy()
values['spending'] = parse_spending()
values['alcohol'] = parse_alcohol()
values['cigarettes'] = parse_cigarettes()
values['traffic'] = parse_traffic()
values['gdp'] = parse_gdp()
values['ppp'] = parse_ppp()
values['cars'] = parse_cars()
values['household'] = parse_cars()

#print(parse_household())
#values['ppp'] = parse_ppp()

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

#}}}

# {{{ normalizing fns
def make_normalized(vals):
    mean = sum(vals.values())/len(vals)
    sigma = math.sqrt(sum((v - mean) ** 2 for v in vals.values()) / len(vals))
    return mean, sigma, {k : (v - mean) / sigma for k, v in vals.items()}

def unnormalize(val, mean, sigma):
    return val * sigma + mean
#}}}

#{{{ extend
def extend(values, deg):

    def map_dict(values, fn):
        res = {}
        for country, val in values.items():
            res[country] = fn(val)
        return res

    res = {}
    for feature in values:
        for i in range(1, deg+1):
            res['%s_%d'%(feature, i)] = map_dict(values[feature], lambda x: x**i)
        res['spending_log'] = map_dict(values['spending'], lambda x: math.log(x))
        res['gdp_log'] = map_dict(values['gdp'], lambda x: math.log(x))
        res['ppp_log'] = map_dict(values['ppp'], lambda x: math.log(x))
    return res
#}}}

def prepare_for_ml(values, normalized, countries, country_tbp, xfeatures, yvalues):
    x = []
    y = []
    for country in countries:
        if country_equal(country, country_tbp):
            continue
        gdp = get_value(values['gdp'], country)
        if gdp < 1000:
            print('skipping %s'%country)
            continue
        xx = []
        for feature in xfeatures:
            xx.append(get_value(normalized[feature]['values'], country))
        x.append(xx)
        y.append(get_value(yvalues, country))
    px = []
    for feature in xfeatures:
        px.append(get_value(normalized[feature]['values'], country_tbp))

    return x, y, [px], get_value(yvalues, country_tbp)

xvalues = {}
yvalues = None
all_features = ['life_expectancy', 'spending', 'alcohol', 'cigarettes', 'traffic', 'gdp', 'cars',
        'household', 'ppp']
feature_tbp = 'life_expectancy'
features_x = [feature for feature in all_features if feature != feature_tbp]
country_tbp = 'Slovak Republic'
#country_tbp = 'Switzerland'
country_tbp = 'Vietnam'

for feature in all_features:
    if feature != feature_tbp:
        xvalues[feature] = values[feature]
    else:
        yvalues = values[feature]

xvalues = extend(xvalues, 1)
xfeatures = list(xvalues.keys())

not_have = set()
for country in values['life_expectancy']:
    for values_names in all_features:
        if get_value(values[values_names], country) == None:
            not_have.add(country)

normalized = {}
for feature in xvalues:
    mean, sigma, norm_values = make_normalized(xvalues[feature])
    entry = {
      'mean': mean,
      'sigma': sigma,
      'values': norm_values,
    }
    normalized[feature] = entry

countries = list(set(values['life_expectancy'].keys()) - not_have)

x, y, px, res = prepare_for_ml(values, normalized, countries, country_tbp, xfeatures, yvalues)

clf = linear_model.LinearRegression()
print(clf.fit(x, y))

coef = {feature: clf.coef_[i] for i, feature in enumerate(xfeatures)}
print(coef)

predict = clf.predict(px)

print(predict, get_value(values[feature_tbp], country_tbp))

#from sklearn import svm
#X = [[0, 0], [1, 1]]
#y = [0, 1]
#clf = svm.SVC()
#print(clf.fit(X, y))
