# coding:utf-8
import re
import time
import warnings
import argparse
import urllib.request as UR
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs

warnings.filterwarnings("ignore")
FLAGS = None

web_address = "http://tianqi.2345.com"
cols = [ 'region',
         'date',
         'bWendu',
         'yWendu',
         'tianqi',
         'fengxiang',
         'fengli',
         'aqi',
         'aqiInfo',
         'aqiLevel']
aqi_dict = {'优':1, '良':2, '轻度污染':3, '中度污染':4, '重度污染':5, '严重污染':6}

def replaceCH(string):
    new_string = ''
    for s in string:
        if s == r'月':
            new_string += '-'
        elif s == r'日':
            new_string += ''
        else:
            new_string += s
    return new_string

def getForcast(city_py, city_code):
    url = web_address+"/"+city_py+"/"+city_code+".htm"
    req = UR.Request(url)
    # 添加表头，模拟浏览器
    req.add_header('User-Agent', 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)')
    response = UR.urlopen(req)
    html = response.read()
    # bs4解析html
    soup = bs(html, 'html.parser')
    city_name = soup.find('a', id="lastBread").text.split("天气")[0]
    bWendu = [int(it.text.split('℃')[0].split('～')[-1])
              for it in soup.find("div", class_="wea-detail").find_all('i')]
    yWendu = [int(it.text.split('℃')[0].split('～')[0] )
              for it in soup.find("div", class_="wea-detail").find_all('i')]
    tianqi = [it.text
              for it in soup.find("div", class_="wea-detail").find_all('b')]
    fengli = [it.text.split('℃')[-1].strip().split('风')[-1].strip()
              for it in soup.find("div", class_="wea-detail").find_all('i')]
    fengxiang = [it.text.split('℃')[-1].strip().split('风')[0].strip()
                 for it in soup.find("div", class_="wea-detail").find_all('i')]
#     date1 = [it.text.strip() for it in soup.find("div", class_="wea-detail").find_all('strong')]
    # 空气质量数据在另一个页面获取
    aqi_url_tail = soup.find('div', class_="kqi-tips").a['href']
    url_aqi = web_address+aqi_url_tail
    req_aqi = UR.Request(url_aqi)
    # 添加表头，模拟浏览器
    req_aqi.add_header('User-Agent', 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)')
    req_aqi.add_header("Referer", url)
    response_aqi = UR.urlopen(req_aqi)
    html_aqi = response_aqi.read()
    # bs4解析html
    soup_aqi = bs(html_aqi, 'html.parser')
    date = [d.span.text.split("(")[0] for d in soup_aqi.find_all("div", class_="td td1")]
    aqiInfo = [d.i.string for d in soup_aqi.find_all("div", class_="td td2")]
    aqi = [int(d.span.string) for d in soup_aqi.find_all("div", class_="td td3 tc")]
    aqiLevel = [aqi_dict[i] for i in aqiInfo]
    date = ['2019-'+replaceCH(d) for d in date]

    wea_forcast_df = pd.DataFrame(columns=cols)
    wea_forcast_df['region'] = [city_name]*len(date)
    wea_forcast_df['date'] = date
    wea_forcast_df['bWendu'] = bWendu
    wea_forcast_df['yWendu'] = yWendu
    wea_forcast_df['tianqi'] = tianqi
    wea_forcast_df['fengxiang'] = fengxiang
    wea_forcast_df['fengli'] = fengli
    wea_forcast_df['aqi'] = aqi
    wea_forcast_df['aqiInfo'] = aqiInfo
    wea_forcast_df['aqiLevel'] = aqiLevel
    return wea_forcast_df

def getHistory(city, month):
    request = UR.Request("http://tianqi.2345.com/t/wea_history/js/{m}/{c}_{m}.js".format(m=month, c=city))
    request.add_header("Referer", "http://tianqi.2345.com/wea_history/{c}.htm".format(c=city))
    request.add_header('User-Agent', 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)')
    response = UR.urlopen(request)
    html = response.read().decode("gbk")
    content = str.split(html,"=")[1].split("]")[0].split("tqInfo:[")[-1]
    re_object = re.findall("{.*?}", content)
    city_name = html[html.find('city')+6:html.find('tqInfo')-2]
    date = []
    bWendu = []
    yWendu = []
    tianqi = []
    fengxiang = []
    fengli = []
    aqi = []
    aqiInfo = []
    aqiLevel = []
    for s in re_object[:-1]:
        date.append(s[s.find('ymd')+5:s.find('bWendu')-2])
        bWendu.append(re.findall('\d+', s[s.find('bWendu')+8:s.find('yWendu')-2])[0])
        yWendu.append(re.findall('\d+', s[s.find('yWendu')+8:s.find('tianqi')-2])[0])
        tianqi.append(s[s.find('tianqi')+8:s.find('fengxiang')-2])
        fengxiang.append(s[s.find('fengxiang')+11:s.find('fengli')-2])
        fengli.append(s[s.find('fengli')+8:s.find('aqi')-2])
        aqi.append(s[s.find('aqi')+5:s.find('aqiInfo')-2])
        aqiInfo.append(s[s.find('aqiInfo')+9:s.find('aqiLevel')-2])
        aqiLevel.append(s[s.find('aqiLevel')+10:s.find('}')-1])
    weather_df = pd.DataFrame()
    weather_df['region'] = [city_name]*len(date)
    weather_df['date'] = date
    weather_df['bWendu'] = bWendu
    weather_df['yWendu'] = yWendu
    weather_df['tianqi'] = tianqi
    weather_df['fengxiang'] = fengxiang
    weather_df['fengli'] = fengli
    weather_df['aqi'] = aqi
    weather_df['aqiInfo'] = aqiInfo
    weather_df['aqiLevel'] = aqiLevel
    return weather_df

def main():
    _cityCode = FLAGS.cityCode
    _cityPy = FLAGS.cityPinyin
    _month = FLAGS.month
    _range = FLAGS.range
    if _range == 'f':
        weather_df = getForcast(_cityPy, _cityCode)
        weather_df.to_csv("./Forecast_"+_cityPy+"_"+_cityCode+".csv", index=False)
    else:
        weather_df = getHistory(_cityCode, _month)
        weather_df.to_csv("./History_"+_cityCode+"_"+_month+".csv", index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--citycode', type=str, default='58457', help='City code, like 58457 represents 杭州')
    parser.add_argument('--citypinyin', type=str, default='hangzhou', help='City pinyin, like hangzhou represents 杭州')
    parser.add_argument('--month', type=str, default='201901', help='Month information like: 201901')
    parser.add_argument('--range', type=str, default='f', help='Get history weather or weather forecast, h represents history and f for forecast')
    FLAGS, unparsed = parser.parse_known_args()
    main()