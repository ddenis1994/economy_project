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
    [(30, 39), 0.10, 0.10],
    [(40, 49), 0.01, 0.07],
    [(50, 59), 0.05, 0.05],
    [(60, 67), 0.03, 0.03]]
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

# version 2.5

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
def to_quit(p, a, staying_probability, i):
    if p <= 0:
        return 0
    return p * staying_probability * leave_rate[a + i + 1]


'''
last salary = ls
seniority =s,
salary growth rate = sg
discount rate = d
age = a
gender =g

'''


def to_die(ls, sg, d, a, g, t, staying_probability):
    return ls * staying_probability * deadRate(a + t, g) * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]),
                                                                                      t + 0.5)


def to_fired(ls, sg, d, a, t, staying_probability):
    return ls * staying_probability * fire_rate[a + t] * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]),
                                                                                    t + 0.5)


'''
prasange 14=p
senority =s
startWord =sw
data of recive 14 prasantage =d
'''


def percentage(sw, p, s, d):
    long = 0
    if d.year != 0:
        long = d.year - sw.year
    if math.isnan(p):
        return s
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
    id = row[0]
    first_name = row[1]
    last_name = row[2]
    empoyment_date = row[5]
    age = row[15]
    gender = row[3]
    ageToRetire = year_to_retire(age, gender)
    _property = row[9]
    last_salary = row[6]
    percentage_of_clause14 = row[8] / 100
    date_of_clause14 = row[7]
    seniority = row[16]
    _sum = 0
    salary_growth_rate_index = 0
    new_seniority = percentage(empoyment_date, percentage_of_clause14, seniority, date_of_clause14)
    try:
        if seniority <= 2:
            _property = 0
        if ageToRetire > 0:
            staying_probability = 1
            for i in range(ageToRetire):
                if i % 2 == 0 and i != 0:
                    salary_growth_rate_index += 1
                staying_probability = staying_probability * to_remain_next_year(age + i, gender)
                _sum += \
                    to_quit(_property, age, staying_probability, i) + \
                    new_seniority * to_die(last_salary, up_salary_rate, salary_growth_rate_index, age, gender, i,
                                           staying_probability) + \
                    new_seniority * to_fired(last_salary, up_salary_rate, salary_growth_rate_index, age, i,
                                             staying_probability)
        else:
            return last_salary * seniority
    except Exception:
        print(Exception)
        print("error")
    print("{} : {} {} {} ".format(id, first_name, last_name, _sum))
    return _sum


x = data.apply(lambda x: mainFunc(x.tolist()), axis=1)
sums = 0
for i in list(x):
    sums += i
print("the total sum : {}".format(sums))

# def retirementAgeGender(Gender):
#
#     if Gender == 'm' or 'M':
#         return 67
#     if Gender == 'f' or 'F':
#         return 64
#
# def MainFunction(row):
#     ID=row[0]
#     FirstName=row[1]
#     LastName=row[2]
#     Gender=row[3]
#     Age=row[15]
#     EmpoymentDate=row[5]
#     LastSalary=row[6]
#     DateOfClause14=row[7]
#     PercentageOfClause14=row[8]
#     Property=row[9]
#     Seniority=row[16]
#     SalaryGrowthRate=0.04
#     RetirementAgeGender=retirementAgeGender(Gender)
#     StayingProbability=1
#     Sum=0
#     Clause14Senority=
#
#     if RetirementAgeGender-Age<=0:
#         return LastSalary*Seniority
#     for t in range (RetirementAgeGender-Age):
#         if t>0:
#             StayingProbability = StayingProbability*(1-FiredProbability-QuittingProbability-DyingProbability)
#             Sum+=Fired(LastSalary, Seniority, PercentageOfClause14, StayingProbability, FiredProbability, DiscountRate, Age, t)+ Quit(StayingProbability, Property, QuitProbability, t, Age)+Died(LastSalary, Seniority, PercentageOfClause14, StayingProbability, DyingProbability, DiscountRate, Age, t)
#     return sum
#
# def Quit(StayingProbability, Property, QuitProbability,t):
#     return Property*QuitProbability(Age+t)*StayingProbability
#
# def Fired(LastSalary, Seniority, PercentageOfClause14, StayingProbability, FiredProbability, DiscountRate, Age, t):
#     return LastSalary*Seniority*Clause14Senority*(pow(1.04,t+0.5)*StayingProbability*FiredProbability(Age+t))/pow(1+DiscountRate,t+0.5)
#
# def Died(LastSalary, Seniority, PercentageOfClause14, StayingProbability, DyingProbability, DiscountRate, Age, t):
#     return LastSalary*Seniority*Clause14Senority*(pow(1.04,t+0.5)*StayingProbability*DyingProbability(Age+t))/pow(1+DiscountRate,t+0.5)
#
# def Clause14Senority():
#     def prasange(EmpoymentDate, p, s, DateOfClause14):
#     if DateOfClause14.year != 0:
#         NewSeniority = DateOfClause14.year - EmpoymentDate.year
#     else:
#         NewSeniority = 0
#     return (NewSeniority * (1 - PercentageOfClause14) + (Seniority - NewSeniority))
#
# def QuitProbability(Age):
#     return go to excel file according to age
#
# def FiredProbability(Age):
#     return go to excel file according to age
#
# def DyingProbability(Age):
#     return go to excel file according to age
