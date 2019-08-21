# encoding = utf-8
import numpy as np
import pandas as pd
import chinese_calendar as cc
from tqdm import tqdm


def _create_empty_list(num):
    """ 创建指定数量的空列表.
    
    用于初始化指定数量的空列表.
    
    Args:
        num: 空列表数量.
    
    Returns:
        返回指定数量的空列表;例如:
        
        当num为3时,返回: [], [], [].
    """
    if num <=0:
        return
    if num == 1:
        return []
    else:
        return [], _create_empty_list(num-1)

def build_date_fea_defult(df, date_col):
    """ 构建日期相关特征.
    
    为一个DataFrame的日期列构造日期相关特征,
    构建的特征有:
        ['year', 'month', 'day','dayofyear', 
         'dayofweek', 'daysinmonth', 'is_leap_year', 
         'is_in_lieu', 'is_holiday', 'is_workday'].
    
    Args:
        df: 输入的DataFrame.
        date_col: 日期列名,为一个字符串,需存在于df中,对应列可以是字符串格式或者日期格式.
    
    Returns:
        df: 构建完成的新的DataFrame.
    """
    year, month, day, dayofyear, \
    dayofweek, daysinmonth, is_leap_year,  \
    is_in_lieu, is_holiday, is_workday = _create_empty_list(10)
    for t in df[date_col]:
        t = pd.to_datetime(t)
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
    """ 构建日期相关特征.
    
    为一个DataFrame的日期列构造日期相关特征,如是否节假日等.
    
    Args:
        df: 输入的DataFrame.
        date_col: 日期列名,为一个字符串,需存在于df中,对应列可以是字符串格式或者日期格式.
        features: 需要构建的特征名称列表,为一个字符串列表,
            字符串对应的方法应该存在于日期可调用方法中或者chinesecalendar包中;
            默认值为['year', 'month', 'day', 'is_in_lieu', 'is_holiday', 'is_workday'], 
            还可以添加诸如:'dayofyear', 'dayofweek', 'daysinmonth', 'is_leap_year'等.
    
    Returns:
        df: 构建完成的新的DataFrame.
    """
    for f in features:
        locals()[f] = []
    for t in tqdm(df[date_col]):
        t = pd.to_datetime(t)
        for f in features:
            try:
                locals()[f].append(int(getattr(t, f)))
            except:
                locals()[f].append(int(getattr(cc, f)(t)))
    for f in features:
        df[f] = locals()[f]
    return df


def recode(df, col):
    """ 重新编码某一列.
    
    将一个DataFrame的某一列(字符类型)重新编码为整型id.
    
    Args:
        df: 输入的DataFrame.
        col: 待编码的列名,需存在于df中.
    
    Returns:
        df: 返回重新编码之后的DataFrame.
    """
    vunique = df[col].unique()
    vdic = {vunique[i]:i for i in range(len(vunique))}
    new_col = [vdic[i] for i in df[col]]
    df[col] = new_col
    return df


def tolibsvm(df):
    """ 将一个DataFrame转化为libsvm格式.
    
    Args:
        df: 输入的DataFrame.
    
    Returns:
        cols_dic: 输入的DataFrame的列名的编号字典.
        line_list: libsvm格式的数据.
    """
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


def resplit(file, col, sp_old, sp_new):
    """csv文件处理,重新设置csv文件的分隔符.
    
    当csv文件读取失败,提示文档中某一行存在更多分隔符时,
    确定是哪一列内容存在分隔符,即可调用本方法.
    
    Args:
        file: csv文件名.
        col: 内容存在分隔符的列是第几列.
        sp_old: 原始分隔符,无默认值,csv原始默认分隔符为','.
        sp_new: 新的分隔符,需要区别于原始分隔符.
    
    Returns:
        new_file: 返回新的文件名.
    """
    count = -1
    new_res = list()
    with open(file, 'r') as f:
        for line in tqdm(f):
            tmp_count = line.count(sp_old)
            if count == -1:
                count = tmp_count
            if tmp_count == count:
                new_line = line
            else:
                delta = tmp_count - count + 1
                sps = line.split(sp_old)
                new_line = sp_new.join(sps[:col] + [sp_old.join(sps[col:col+delta])] + sps[col+delta:])
            new_res.append(new_line)
    new_file = '.'.join(file.split('.')[:-1])+'_fmt.csv'
    with open(new_file, 'w') as f:
        for nl in new_res:
            f.write(nl)
    return new_file
