# encoding = utf-8

import numpy as np
import pandas as pd
import chinese_calendar as cc
from tqdm import tqdm


def _create_empty_list(num):
    if num <=0:
        return
    if num == 1:
        return []
    else:
        return [], _create_empty_list(num-1)

def build_date_fea_defult(df, date_col):
    year, month, day, dayofyear, \
    dayofweek, daysinmonth, is_leap_year,  \
    is_in_lieu, is_holiday, is_workday = _create_empty_list(10)
    for t in df[date_col]:
        year.append(t.year)
        month.append(t.month)
        day.append(t.day)
        dayofyear.append(t.dayofyear)
        dayofweek.append(t.dayofweek)
        daysinmonth.append(t.daysinmonth)
        is_leap_year.append(int(t.is_leap_year))
        is_in_lieu.append(int(cc.is_in_lieu(t)))
        is_holiday.append(int(cc.is_holiday(t)))
        is_workday.append(int(cc.is_workday(t)))
    df['year'] = year
    df['month'] = month
    df['day'] = day
    df['dayofyear'] = dayofyear
    df['dayofweek'] = dayofweek
    df['daysinmonth'] = daysinmonth
    df['is_leap_year'] = is_leap_year
    df['is_in_lieu'] = is_in_lieu
    df['is_holiday'] = is_holiday
    df['is_workday'] = is_workday
    return df
    
    
# build date features of self-defined cats
def build_date_fea_selfdefine(df, 
                        date_col, 
                        features = ['year', 'month', 'day', 'is_in_lieu', 'is_holiday', 'is_workday']):
    for f in features:
        locals()[f] = []
    for t in tqdm(df[date_col]):
        for f in features:
            try:
                locals()[f].append(int(getattr(t, f)))
            except:
                locals()[f].append(int(getattr(cc, f)(t)))
    for f in features:
        df[f] = locals()[f]
    return df


def recode(df, col):
    vunique = df[col].unique()
    vdic = {vunique[i]:i for i in range(len(vunique))}
    new_col = [vdic[i] for i in df[col]]
    df[col] = new_col
    return df


def tolibsvm(df):
    cols_dic = {df.columns[i]:str(i) for i in range(0, len(df.columns))}

    line_list = list()
    for i in tqdm(range(len(df))):
        j = 0
        line = ''
        for v in df.loc[i].values:
            line += ' '+str(j)+':'+str(v)
            j += 1
        line_list.append(line)

    return cols_dic, line_list