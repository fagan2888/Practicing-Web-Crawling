'''
id: int
item: str
total_buy: int
total_sell: int
difference: int
date: datetime
'''
from pymongo import MongoClient
import pymongo
from datetime import date, timedelta, datetime
import json
import pandas as pd
import numpy as np
from bson.objectid import ObjectId
import pprint
from tqdm import tqdm
import time


url = 'http://www.twse.com.tw/fund/BFI82U?response=html&dayDate={0}&weekDate={0}&monthDate={0}&type=day'

def getTradeValue(dt):
    data = pd.read_html(url.format(dt))[0]
    data.columns = data.columns.droplevel()
    return data

def str_to_json(x):
    dictionary = x.replace("'", "\"")
    data = json.loads(dictionary)
    return data


def main():
    client = MongoClient('mongodb://finance:27017/')
    db = client.stock
    collect = db['institutional-investors-trading-values']

    requestDate = datetime(2016, 1, 1)
    crawled = []

    # reset collection
    collect.delete_many({})

    runs = (datetime.today() - requestDate).days
    pbar = tqdm(total = runs+1)
    while requestDate < datetime.today():
        requestDate = requestDate + timedelta(days=1)
        day = datetime.strftime(requestDate, '%Y-%m-%d')
        time.sleep(5)
        try: 
            data = getTradeValue(day.replace('-', ''))
            data['date'] = day
            data.columns = ['institution', 'total_buy', 'total_sell', 'net', 'date']
            crawled.extend(data.apply(lambda s: str_to_json(s.to_json()), axis=1).values.tolist())
            pbar.update(1)
        except:
            continue

    pbar.close()
    print(crawled)
    collect.insert_many(crawled)


    # count the amount of data in collection
    i = 0
    for j in collect.find():
        i += 1
    print(i)


if __name__ == "__main__":
    main()