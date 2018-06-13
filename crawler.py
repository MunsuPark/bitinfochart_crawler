import os
import shutil
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

target_url = "https://bitinfocharts.com/comparison/{coin}-{index}.html"
coins = ['btc', 'eth', 'btg', 'bch', 'ltc', 'etc', 'xrp']
traget_indexs = [
    'transactions', 'size', 'sentbyaddress', 'difficulty', 'hashrate', 'price', 'mining_profitability',
    'sentinusd', 'transactionfees', 'median_transaction_fee', 'confirmationtime', 'marketcap', 'transactionvalue',
    'mediantransactionvalue', 'tweets', 'activeaddresses'
]
xrp_target_indexs = ['transactions', 'price', 'transactionfees', 'marketcap', 'tweets']


def get_dataframe_from_url(coin, index):
    url = target_url.format(coin=coin, index=index)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    date_index_info_str = soup.body.find_all('div')[8].find_all('script')[2].text.split(';')[16]
    date_index_infos = date_index_info_str[
                       date_index_info_str.index(',') + 1:date_index_info_str.index('{') - 2].replace('[', '').replace(
        ']', '').replace('new Date("', '').replace('")', '').split(',')
    info_dict = {}
    is_date, date = True, None
    for info in date_index_infos:
        if is_date:
            date = info
            is_date = not is_date
        else:
            value = float(info) if info != 'null' else None
            info_dict[date] = value
            is_date = not is_date
    return pd.DataFrame(list(info_dict.items()), columns=['date', index])


def get_multiple_index_dateframe(coin):
    indexs = traget_indexs if coin != 'xrp' else xrp_target_indexs
    result = get_dataframe_from_url(coin, indexs[0])
    print("{} {} finished".format(coin, indexs[0]))
    for i in range(1, len(indexs)):
        df = get_dataframe_from_url(coin, indexs[i])
        print("{} {} finished".format(coin, indexs[i]))
        result = pd.merge(left=result, right=df, how='left', on='date')
    return result


def make_zip():
    os.makedirs("tmp")

    for coin in coins:
        df = get_multiple_index_dateframe(coin)
        df.to_csv("tmp/{}.csv".format(coin))
        print("{} finished!".format(coin))
    shutil.make_archive("{}".format(datetime.today().strftime('%Y%m%d')), 'zip', 'tmp')
    shutil.rmtree("tmp")
