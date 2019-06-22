import re
import math
from sklearn import linear_model
# from sklearn import svm
# from sklearn.preprocessing import PolynomialFeatures

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

def expand(vals, deg):
    res = {}
    for k, v in vals.items():
        for i in range(deg):
            res['%s_%d'%(k, i)] = v ** i
        if k == 'spending':
            res['spending_log'] = math.log(v)
    return res

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


not_have = set()
for country in values['life_expectancy']:
    for values_names in ['spending', 'alcohol', 'cigarettes', 'traffic']:
        if get_value(values[values_names], country) == None:
            not_have.add(country)

countries = list(set(values['life_expectancy'].keys()) - not_have)

country_tbp = 'Slovak Republic'
#country_tbp = 'Switzerland'
#country_tbp = 'Vietnam'

features_x = ['spending', 'cigarettes', 'alcohol', 'traffic']
#features_x = ['life_expectancy']
feature_tbp = 'life_expectancy'
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

print(x)
x = expand(x, 3)
px = expand(px, 3)

#clf = svm.SVR(kernel = 'poly', degree = 1, C=1e4)
#poly = PolynomialFeatures(degree=2)
#x = poly.fit_transform(x)
#px = poly.fit_transform(px)

#clf = svm.SVR(kernel='rbf', C=1e3, gamma=0.1)
#[ 0.46175588  0.23330927 -0.09097151 -0.18364082]
clf = linear_model.LinearRegression()
print(clf.fit(x, y))
print(clf.score(x,y))
#print(clf.coef_, clf.intercept_)
#print(dir(clf))

predict = clf.predict(px)

print(predict, get_value(values[feature_tbp], country_tbp))

#from sklearn import svm
#X = [[0, 0], [1, 1]]
#y = [0, 1]
#clf = svm.SVC()
#print(clf.fit(X, y))

#print(re.sub(r'def\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*\(\s*\):', r'static PyObject*\npy_\1(void)\n{', 'def myfunc():'))
