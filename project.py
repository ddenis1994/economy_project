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
    [(60, 67), 0.03, 0.03],
    [(68, 110), 1, 1]]
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

# data = (data[data['reason'].isna()]).reset_index()
data = data.reset_index()

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
        if g in ['final']:
            return 1
    raise Exception("cannot determine the gender")


def toRemain(age, dead):
    return 1 - fire_rate[age] - leave_rate[age] - dead


# tPx
def to_remain_next_year(age, g):
    return toRemain(age, deadRate(age, g))


# p = property
# a=age
# g=gender
def to_quit(p, a, staying_probability, i):
    if p <= 0:
        return 0
    temp = leave_rate[a + i]
    return p * staying_probability * temp


'''
last salary = ls
seniority =s,
salary growth rate = sg
discount rate = d
age = a
gender =g

'''


def to_die(ls, sg, d, a, g, t, staying_probability):
    temp = deadRate(a + t, g)
    return ls * staying_probability * temp * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]),
                                                                        t + 0.5)


def to_die2(ls, seniority, dieRate, salary_groth_rate, year, toStay):
    return toStay * ls * seniority * dieRate * pow(1 + salary_groth_rate, year + 0.5) / pow(
        (1 + assumption['rate'][year + 1]),
        year + 1 + 0.5)


def to_fired2(ls, seniority, staying_probability, alary_groth_rate, year, fireRate):
    down = (1 + assumption['rate'][year + 1])
    newYear = year + 0.5
    return (ls * staying_probability * seniority * fireRate * pow(1 + alary_groth_rate, newYear) \
            / pow(down, newYear))


def to_fired(ls, sg, d, a, t, staying_probability):
    temp = fire_rate[a + t + 1]
    return ls * staying_probability * temp * pow(1 + sg, d + 0.5) / pow((1 + assumption['rate'][t + 1]),
                                                                        t + 0.5)


'''
prasange 14=p
senority =s
startWord =sw
data of recive 14 prasantage =d
'''


def percentage(sw, p, s, d):
    # check if the employ has section 14
    if p == 0:
        return s
    # how long the person didn't had the section 14
    long = 0
    if d is not None:
        long = d.year - sw.year
    # how much time the employ has section 14 * the section 14
    # and how much years the employ didn't has section 14
    return (s - long) * (1 - p) + long


def year_to_retire(age, g):
    if 17 < age < 111:
        if g in ['M', 'm']:
            return 67 - age
        if g in ['F', 'f']:
            return 64 - age
    raise Exception("cannot determine the gender")


def factor(_sum, last_salary, sonority, parentage14):
    return _sum / last_salary * sonority * parentage14


def service_currant(last_selaty, part_year, prantage14, factor):
    return last_selaty * part_year * prantage14 * factor


def service_expance(ageToRetire, age, gandaer):
    result = 0
    for i in range(ageToRetire):
        result += math.pow(to_remain_next_year(age + i, gandaer), i)
    return result


# עלות יייון
def cost_of(sum, shior_yevon, halot_serot, hatabot):
    return sum * shior_yevon + (halot_serot - hatabot) * shior_yevon / 2


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
    _id = row[0]
    first_name = row[1]
    last_name = row[2]
    employment_date = row[5]
    age = row[15]
    gender = row[3]
    _property = row[9]
    last_salary = row[6]
    percentage_of_clause14 = row[8] / 100
    date_of_clause14 = row[7]
    seniority = row[16]
    paid = row[12]
    zak = row[13]
    leave_data = row[11]

    # custom data
    ageToRetire = year_to_retire(age, gender)

    # <editor-fold desc="normalize data for use">
    if pan.isna(row[14]):
        fire_reason = True
    else:
        fire_reason = False
    if math.isnan(paid):
        paid = 0
    if math.isnan(zak):
        zak = 0
    if isinstance(leave_data, float):
        if math.isnan(leave_data):
            leave_data = None
    if isinstance(leave_data, str or pan.NaT or math.nan):
        leave_data = None
    if pan.isna(date_of_clause14):
        date_of_clause14 = None
    if pan.isna(percentage_of_clause14):
        percentage_of_clause14 = 0
    # </editor-fold>

    start_value = 200000

    # array of result start
    result = [_id, start_value]
    _sum = 0
    # calculate tree if worker still works
    if fire_reason is True:
        salary_growth_rate_index = 0
        try:
            # if the worker doesnt have 2 year at the work
            if seniority <= 2:
                _property = 0
            # if the worker have years to work and he has seniority of over 2 years
            elif ageToRetire > 0:
                # in case the worker has section 14
                localSeniority = percentage(employment_date, percentage_of_clause14, seniority, date_of_clause14)
                if localSeniority != 0:
                    staying_probability = 1
                    for yearToRetire in range(ageToRetire):
                        if yearToRetire % 2 == 0 and yearToRetire != 0:
                            salary_growth_rate_index += 0.04
                        # not to change in first iteration
                        if yearToRetire != 0:
                            staying_probability *= to_remain_next_year(age + yearToRetire, gender)
                        # calculate the quit amount
                        quit_value = to_quit(_property, age, staying_probability, yearToRetire)
                        # calculate the die amount
                        toDieRate = deadRate(age + yearToRetire, gender)
                        die_value = to_die2(last_salary, localSeniority, toDieRate, salary_growth_rate_index,
                                            yearToRetire,
                                            staying_probability)
                        # calculate the fired amount
                        toFireRate = fire_rate[age + yearToRetire + 1]
                        fire_value = to_fired2(last_salary, localSeniority, staying_probability,
                                               salary_growth_rate_index,
                                               yearToRetire, toFireRate)
                        # the yearly sum for the worker
                        _sum += \
                            quit_value + die_value + fire_value
                        print(_sum,yearToRetire)
                    print("end")
                else:
                    _sum = 2
            # _sum += \
            #     quit_value + die_value + fire_value
            # temp = yearToRetire
            # _sum += \
            #     to_quit(_property, 68, staying_probability, temp) + \
            #     new_seniority * to_die(last_salary, up_salary_rate, salary_growth_rate_index, age, 'final', temp,
            #                            staying_probability) + \
            #     new_seniority * to_fired(last_salary, up_salary_rate, salary_growth_rate_index, 68, temp,
            #                              staying_probability)

        except Exception:
            print(Exception)
            print("error")
    # else:
    #     return last_salary * seniority

    # print("{} : {} {} {} ".format(_id, first_name, last_name, _sum))
    # print(paid)
    result += [_sum]
    # if percentage_of_clause14 != 1:
    #     h = round(service_expance(ageToRetire, age, gender))
    #     factor2 = factor(_sum, last_salary, seniority, (1 - percentage_of_clause14))
    #     sv = service_currant(last_salary, 0.5, (1 - percentage_of_clause14), factor2)
    #     result += [sv]
    #     temp2 = 0
    #     if h != 0:
    #         temp2 += cost_of(_sum, assumption['rate'][h], sv, paid)
    #     else:
    #         temp2 += cost_of(_sum, 1, sv, paid)
    #     result += [temp2]
    #     hatavot = 0
    #     if not math.isnan(paid):
    #         hatavot += paid
    #     if not math.isnan(zak):
    #         hatavot += zak
    #     result += [hatavot]
    #     result += [_sum]
    #     result += [_sum - start_value - sv - temp2 + hatavot]

    return result


t = data.to_dict()
x = data.apply(lambda x: mainFunc(x.tolist()), axis=1)
sums = 0
for i in list(x):
    print(i)
    sums += i[2]
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
