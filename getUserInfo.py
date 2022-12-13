# -*-coding:utf8-*-

import datetime
import json
import random
import sys
import time
from importlib import reload
from multiprocessing.dummy import Pool as ThreadPool

#import pymysql
import psycopg2
import requests


# def datetime_to_timestamp_in_milliseconds():
    # def current_milli_time(): return int(round(time.time() * 1000))

    # return current_milli_time()


reload(sys)


def LoadUserAgents(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[:-1])
    random.shuffle(uas)
    return uas


uas = LoadUserAgents("user_agents.txt")
head = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/93.0.4577.82 Safari/537.36 Edg/93.0.961.52',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'https://space.bilibili.com/37208321',
    'Origin': 'https://space.bilibili.com',
    'Host': 'space.bilibili.com',
    'AlexaToolbar-ALX_NS_PH': 'AlexaToolbar/alx-4.0',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

# Please replace your own proxies.
proxies = {
    # 'http': 'http://120.26.110.59:8080',
    # 'http': 'http://120.52.32.46:80',
    # 'http': 'http://218.85.133.62:80',
}
time1 = time.time()

urls = []

# Please change the range data by yourself.
for m in range(400, 401):
    for i in range (m*100 , (m+1)*100):
        url = 'https://space.bilibili.com/' + str(i)
        urls.append(url)
        print('nmsl!')

    def getsource(url):
        payload = {
            # '_': datetime_to_timestamp_in_milliseconds(datetime.datetime.now()),
            'mid': url.replace('https://space.bilibili.com/', '')
        }
        ua = random.choice(uas)
        head = {
            'User-Agent': ua,
            'Referer': 'https://space.bilibili.com/' + str(i) + '?from=search&seid=' + str(random.randint(10000, 50000))
        }
        mid = payload['mid']

        # 使用post会报错 (2021/5/2)
        jscontent = requests \
            .session() \
            .get('https://api.bilibili.com/x/space/acc/info?mid=%s&jsonp=jsonp' % mid,
                 headers=head,
                 data=payload
                 ) \
            .text

        time2 = time.time()
        try:
            jsDict = json.loads(jscontent)
            status_code = jsDict['code'] if 'code' in jsDict.keys() else False
            if status_code == 0:
                if 'data' in jsDict.keys():
                    jsData = jsDict['data']
                    mid = jsData['mid']
                    name = jsData['name']
                    sex = jsData['sex']
                    rank = jsData['rank']
                    face = jsData['face']
                    regtimestamp = jsData['jointime']
                    regtime_local = time.localtime(regtimestamp)
                    regtime = time.strftime("%Y-%m-%d %H:%M:%S", regtime_local)

                    birthday = jsData['birthday'] if 'birthday' in jsData.keys() else 'nobirthday'
                    sign = jsData['sign']
                    level = jsData['level']
                    OfficialVerifyType = jsData['official']['type']
                    OfficialVerifyDesc = jsData['official']['desc']
                    vipType = jsData['vip']['type']
                    vipStatus = jsData['vip']['status']
                    coins = jsData['coins']
                    print("Succeed get user info: " + str(mid) + "\t" + str(time2 - time1))
                    try:
                        res = requests.get(
                            'https://api.bilibili.com/x/relation/stat?vmid=' + str(mid) + '&jsonp=jsonp').text
                        viewinfo = requests.get(
                            'https://api.bilibili.com/x/space/upstat?mid=' + str(mid) + '&jsonp=jsonp').text
                        js_fans_data = json.loads(res)
                        # js_viewdata = json.loads(viewinfo)
                        following = js_fans_data['data']['following']
                        fans = js_fans_data['data']['follower']
                    except:
                        following = 0
                        fans = 0

                else:
                    print('no data now')
                try:
                    print(jsDict)
                    print('nmsl?')
                    # Please write your SQL's information.
                    conn = psycopg2.connect(database="bilibili", user="postgres", password="********", host="localhost", port="9194")
                    print('nmsl~')
                    cur = conn.cursor()
                    # sqlq = 'create table nmsl();'
                    # cur.execute(sqlq)
                    sql = 'INSERT INTO bilibili_user_info values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                    cur.execute(sql,(mid, name, sex, rank, face, regtime, birthday, sign, level, OfficialVerifyType,
                                     OfficialVerifyDesc,vipType, vipStatus, coins, following, fans,))
                    conn.commit()
                except Exception as e:
                    print(e)
            else:
                print("Error: " + url)
        except Exception as e:
            print(e)
            pass

if __name__ == "__main__":
    pool = ThreadPool(1)
    try:
        results = pool.map(getsource, urls)
    except Exception as e:
        print(e)

    pool.close()
    pool.join()
