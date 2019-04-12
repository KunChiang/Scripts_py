# coding:utf-8
import time
import warnings
import urllib.request as UR
import pandas as pd
import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
warnings.filterwarnings("ignore")

def get_onepage(data, url):
    req = UR.Request(url)

    req.add_header('User-Agent', 'Mozilla/4.0(compatible; MSIE 5.5; Windows NT)')
    response = UR.urlopen(req)
    html = response.read()

    soup = bs(html, 'html.parser')
    data = pd.DataFrame(columns=['date','num1','num2','num3','num4','num5','num6','num_blue','sales'])
    for i in range(0,100,5):
        date = soup.find_all('td', align="center")[i].string
        dat2 = pd.to_datetime(date)
        si = soup.find_all('td', align="center")[i+2]
        nums = [int(t.string )for t in si.find_all('em')]
        pri = soup.find_all('tr')[int(i/5+2)].find_all('strong')[0].string
        pri = ''.join(pri.split(','))
        if pri.strip() == '':
            pri = 0
        else:
            pri = int(pri)
        data.loc[len(data)] = [date]+nums+[pri]
    return data

def main():
    data = pd.DataFrame(columns=['date','num1','num2','num3','num4','num5','num6','num_blue','sales'])
    iters = tqdm(range(1, 101))
    for i in iters:
        url = 'http://kaijiang.zhcw.com/zhcw/html/ssq/list_'+str(i)+'.html'
        # print(url)
        data = data.append(get_onepage(data, url))
        time.sleep(np.random.randint(2))
    data.to_csv("./caipiao.csv", index=False)

if __name__ == '__main__':
    main()