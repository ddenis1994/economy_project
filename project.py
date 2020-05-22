import numpy
import pandas as pan
import numpy as np
import math
import datetime

# start load data
up_salary_rate = 0.04
min_trash_hold_for_cup = 2
leave_rate = {}
fire_rate = {}
ages = [
    [(18, 29), 0.15, 0.15],
    [(30, 39), 0.10, 0.1],
    [(40, 49), 0.10, 0.7],
    [(50, 59), 0.5, 0.5],
    [(60, 67), 0.3, 0.3]]
for r in ages:
    for x in range(r[0][0], r[0][1] + 1):
        leave_rate[x] = r[1]
        fire_rate[x] = r[2]

manDeathTable = pan.read_excel('./Death.xlsx', squeeze=True, sheet_name='man', index_col=0, header=0)
womanDeathTable = pan.read_excel('./Death.xlsx', squeeze=True, sheet_name='woman', index_col=0, header=0)

lastDataOfYear = datetime.date(year=datetime.datetime.today().year - 1, month=12, day=31)


def calculate_age(born):
    today = lastDataOfYear
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


data = pan.read_excel('./data3.xlsx', index_col=0, dtype={'שם ': str,
                                                          'שם משפחה': str,
                                                          'מין': str,
                                                          'תאריך לידה': datetime.datetime,
                                                          'תאריך תחילת עבודה ': datetime.datetime,
                                                          'שכר ': float,
                                                          'תאריך  קבלת סעיף 14': datetime.datetime,
                                                          'אחוז סעיף 14': float,
                                                          'שווי נכס': float,
                                                          'הפקדות': float,
                                                          'תאריך עזיבה ': datetime.datetime,
                                                          'תשלום מהנכס': float,
                                                          'השלמה בצ\'ק': float,
                                                          'סיבת עזיבה': str}
                      , header=0,
                      sheet_name='data'
                      , parse_dates=True)

data.rename(columns={'שם ': 'name',
                     'שם משפחה': 'family',
                     'מין': 'sex',
                     'תאריך לידה': 'birth',
                     'שכר ': 'salary',
                     'תאריך תחילת עבודה ': 'startWork',
                     'תאריך  קבלת סעיף 14': 'data14',
                     'אחוז סעיף 14': 'rate14',
                     'שווי נכס': 'property',
                     'הפקדות': 'deposit',
                     'תאריך עזיבה ': 'leaveData',
                     'תשלום מהנכס': 'paidProperty',
                     'השלמה בצ\'ק': 'C',
                     'סיבת עזיבה': 'reason'}, inplace=True)

data['age'] = data.apply(lambda row: calculate_age(row['birth']), axis=1)

assumption = pan.read_excel('./data3.xlsx',
                            sheet_name='assemption',
                            usecols=['year', 'rate'],
                            header=1,
                            index_col=0)

data = (data[data['reason'].isna()]).reset_index()

data['seniority'] = (pan.to_datetime(lastDataOfYear) - pan.to_datetime(data['startWork'])) / np.timedelta64(1, 'Y')
data['seniority'] = data['seniority'].astype(np.int64)


# finish load data


def in_rate(t):
    return pow((1 + up_salary_rate), t + 0.5) / pow((1 + assumption['rate'][t + 1]), t + 0.5)


def leftToWork(g, age):
    if g in ['M', 'm']:
        return 67 - age
    if g in ['F', 'f']:
        return 64 - age


def printData(row):
    mainFunc(leftToWork(row[3], row[15]), row)


def toRemainInWork(row, t):
    if t != 0:
        return 1 - fire_rate[row[15] + t] - leave_rate[row[15] + t] - to_die_next_year(t, row[15], row[3])
    else:
        return 1


def dead(t, row):
    return row[6] * row[16] * (1 - row[8]) * in_rate(t) * tpx(t, row[15], row[3]) * to_die_next_year(t, row[15], row[3])


def fired(t, row):
    return row[6] * row[16] * (1 - row[8]) * in_rate(t) * tpx(t, row[15], row[3]) * to_die_next_year(t, row[15], row[3])


def left(row):
    return leave_rate[row[15]] + row[9] * toRemainInWork(row)


# to die next year at the age : age + t
def to_die_next_year(t, age, gender):
    if 17 < age + t < 111:
        if gender in ['M', 'm']:
            return manDeathTable['q(x)'][age + t + 1]
        if gender in ['F', 'f']:
            return womanDeathTable['q(x)'][age + t + 1]
    raise Exception("cannot determine the gender")


# to be alive from age to age + t
def tpx(t, age, gender):
    if gender in ['M', 'm']:
        return 1 - (manDeathTable['L(x)'][age] - manDeathTable['L(x)'][age + t]) / manDeathTable['L(x)'][age]
    if gender in ['F', 'f']:
        return 1 - (womanDeathTable['L(x)'][age] - womanDeathTable['L(x)'][age + t]) / womanDeathTable['L(x)'][age]


# def mainFunc(time, row):
#     sum = 0
#     for i in range(time):
#         sum += left(row) + fired(i, row) + dead(i, row)
#     print(sum)
#     print("finish row")


def ribit_deribit(A0, i, t):
    return A0 * math.pow((1 + i), t)


def FutureValue(A0, i, t):
    return ribit_deribit(A0, i, t)


def PresentValue(At, i, t):
    return At / (math.pow((1 + i), t))


def SerialPresentValue(Ai, i, t):
    sum = 0
    for j in range(t):
        sum += PresentValue(Ai, i, j + 1)
    return sum


# print(dead(0.5, i, 0.2, 18, 'F') + 2000 + fired(0.5, i, 0.2, 18, 'F'))


# version 2

def deadRate(age, g):
    if 17 < age < 111:
        if g in ['M', 'm']:
            return manDeathTable['q(x)'][age + 1]
        if g in ['F', 'f']:
            return womanDeathTable['q(x)'][age + 1]
    raise Exception("cannot determine the gender")


def toRemain(age, dead):
    return 1 - fire_rate[age] - leave_rate[age] - dead


def to_remain_next_year(age, g):
    return toRemain(age, deadRate(age, g))


# p = property
# a=age
# g=gender
def to_quit(p, a, g, t):
    a += 1
    mul = 1
    for i in range(1, t):
        mul *= to_remain_next_year(a + i, g)
    return p * mul * leave_rate[a]


'''
last salary = ls
seniority =s,
salary growth rate = sg
discount rate = d
age = a
gender =g

'''


# row[6] * row[16] * (1 - row[8]) * in_rate(t) * tpx(t, row[15], row[3]) * to_die_next_year(t, row[15], row[3])
def to_die(ls, sg, d, a, g, t):
    mul = 1
    for i in range(1, t):
        mul *= to_remain_next_year(a + i, g)
    return ls * mul * deadRate(a, g) * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]), t + 0.5)


def to_fired(ls, sg, d, a, g, t):
    mul = 1
    for i in range(1, t):
        mul *= to_remain_next_year(a + i, g)
    return ls * mul * fire_rate[a] * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]), t + 0.5)


'''
prasange 14=p
senority =s
startWord =sw
data of recive 14 prasantage =d
'''


def prasange(d, p, s, sw):
    if d.year != 0:
        long = d.year - sw.year
    else:
        long = 0
    return (long * (1 - p) + (s - long))


def year_to_retire(age, g):
    if 17 < age < 111:
        if g in ['M', 'm']:
            return 67 - age
        if g in ['F', 'f']:
            return 64 - age
    raise Exception("cannot determine the gender")


'''
row[0] = id
row[1] = first name
row[2] = last name
row[3] = gender
row[4] = birth date
row[5] = employment date
row[6] = last salary
row[7] = date of closure 14
row[8] = percentage of closure 14
row[9] = property
row[15] = age
row[16] = seniority
'''


def mainFunc(row):

    age = row[15]
    gender = row[3]
    ageToRetire = year_to_retire(age, gender)
    property = row[9]
    lastSalary = row[6]
    p14 = row[8] / 100
    sd = row[5]
    d14 = row[7]
    seniority = row[16]
    sum = 0
    d = 0
    p = prasange(sd, p14, seniority, d14)
    try:
        for i in range(ageToRetire - age):
            if i % 2 == 0:
                d += 1
            sum += to_quit(property, age, gender, i) + p * to_die(lastSalary, up_salary_rate, d, age, gender,
                                                                  i) + p * to_fired(
                lastSalary,
                up_salary_rate, d,
                age,
                gender, i)
    except Exception:
        print(Exception)
        print("error")
    print(sum)
    return sum

print(data.to_dict())
#print(list(data.apply(lambda x: mainFunc(x.tolist()), axis=1)))
