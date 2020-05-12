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
    return pow((1 + up_salary_rate), t + 0.5) / pow((1 + assumption['rate'][t]), t + 0.5)


def leftToWork(g,age):
    if g in ['M', 'm']:
        return 67-age
    if g in ['F', 'f']:
        return 64-age



def printData(row):
    mainFunc(leftToWork(row[3],row[15]),row)


def left():
    pass


def mainFunc(time,row):
    '''
     sum=0
    for i in range(time):
        sum+=dead()+fired()
    sum2=0
    for i in range(time):
        sum+=left()
    return salery*vetec*(sum+sum2)
    '''
    sum = 0
    for i in range(time):
        sum += left(row)
    print("finish row")

print(fire_rate)

def left(row):
    return leave_rate[row[15]]+row[9]

data.apply(lambda x: printData(x.tolist()), axis=1)


# new try to make the equsion
def t(t, age, sex, self_passion):
    return in_rate(t) * fire_rate[age] * 1 + in_rate(t) * tpx(t, age, sex) * 1 + leave_rate[age] * self_passion


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


# to be alive from age to age + t
def tpx(t, age, gender):
    if gender in ['M', 'm']:
        return 1 - (manDeathTable['L(x)'][age] - manDeathTable['L(x)'][age + t]) / manDeathTable['L(x)'][age]
    if gender in ['F', 'f']:
        return 1 - (womanDeathTable['L(x)'][age] - womanDeathTable['L(x)'][age + t]) / womanDeathTable['L(x)'][age]


# to die next year at the age : age + t
def to_die_next_year(t, age, gender):
    if 17 < age + t < 111:
        if gender in ['M', 'm']:
            return manDeathTable['q(x)'][age + t + 1]
        if gender in ['F', 'f']:
            return womanDeathTable['q(x)'][age + t + 1]
    raise Exception("cannot determine the gender")


def dead(salary,seniority,t, age, gender, parentage,row):
    return salary*seniority*(1 - parentage) * in_rate(t) * tpx(t, age, gender) * to_die_next_year(t, age, gender)



def fired(salary,seniority,t, age, gender, parentage,row):
    return salary*seniority*(1 - parentage) * in_rate(t) * tpx(t, age, gender) * to_die_next_year(t, age, gender)



# print(dead(0.5, i, 0.2, 18, 'F') + 2000 + fired(0.5, i, 0.2, 18, 'F'))
