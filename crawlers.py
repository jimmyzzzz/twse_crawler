'''
常用的爬蟲函數，資料來源都是twse
[import]
    requests
    pandas as pd
[def]
    get_stock_id_list
    get_etf_id_list
    get_otc_id_list
    get_latest_trading_days
    get_stock_month_price
'''

import requests
import pandas as pd


def get_stock_id_list():
    '''
    取得上市股票名單
    [return] list stock_name_list
    '''
    res = requests.get('https://dts.twse.com.tw/opendata/t187ap03_L.csv')
    res.encoding='utf-8'
    df = pd.read_csv(StringIO(res.text), index_col=['公司代號'])
    stock_name_list = [str(i) for i in df.index]
    
    return stock_name_list


def get_etf_id_list():
    '''
    取得etf名單
    [return] list new_證劵號碼list
    '''
    url = 'https://www.twse.com.tw/zh/ETF/list'
    res = requests.get(url)
    data_string = res.text
    
    dataframe_list = pd.read_html(data_string)
    我們要的交易資料_df = dataframe_list[0]
    證劵號碼list = 我們要的交易資料_df['證券代號'].tolist()
    
    # 分割一些特例
    # case1: '006205(新臺幣)00625K(人民幣)' --> ['006205', '00625K']
    # case2: '00636(新臺幣)00636K(美元)' --> ['00636', '00636K']
    左括號是否已經出現 = False
    new_證劵號碼list = []
    for 證劵號碼 in 證劵號碼list:
        if '(' in 證劵號碼 and ')' in 證劵號碼:
            證劵號碼 = 證劵號碼.replace('(',' ( ')
            證劵號碼 = 證劵號碼.replace(')',' ) ')
            分割後的證劵號碼list = 證劵號碼.split()

            for 分割後的證劵號碼 in 分割後的證劵號碼list:
                if 分割後的證劵號碼 == '(':
                    左括號是否已經出現 = True
                elif 分割後的證劵號碼 == ')':
                    左括號是否已經出現 = False
                elif 左括號是否已經出現:
                    pass
                else:
                    new_證劵號碼list.append(分割後的證劵號碼)
        else:
            new_證劵號碼list.append(證劵號碼)
    
    return new_證劵號碼list


def get_otc_id_list():
    '''
    取得上櫃股票名單
    [return] list 上櫃股票名單_list
    '''
    本國企業_datas_dict = {'stk_code':"",'stk_category':"02",'choice_type':"stk_type",'stk_type':""}
    外國企業_datas_dict = {'stk_code':"",'stk_category':"",'choice_type':"stk_type",'stk_type':	"RR"}
    
    url = 'https://www.tpex.org.tw/web/regular_emerging/corporateInfo/regular/regular_stock.php?l=zh-tw'
    
    res = requests.post(url, data=本國企業_datas_dict)
    res.encoding='utf-8'
    本國企業名單_df = pd.read_html(res.text)[0]
    
    res = requests.post(url, data=外國企業_datas_dict)
    res.encoding='utf-8'
    外國企業名單_df = pd.read_html(res.text)[0]
    
    上櫃股票名單_df = pd.concat([本國企業名單_df,外國企業名單_df])
    上櫃股票名單_list = list(上櫃股票名單_df['股票代號'].apply(str).values)
    
    return 上櫃股票名單_list


def get_latest_trading_days():
    '''
    取得目前最新的交易日日期
    [return] str: exp:'20210917'
    '''
    url = 'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=json&date=&type='
    res = requests.get(url)
    return_dict = res.json()
    return return_dict['date']


def get_stock_month_price(stock_id, year, month):
    '''
    取得股票的某月的股價資料(開高低收成交量)
    [param]
        str stock_id: exp:'1101'
        str year:     exp:'2021'
        str month:    exp:'01'
    [return] 
        dict:         dict_keys(['stat','date','title','fields','data','notes'])
        dict:         {"stat":"很抱歉，沒有符合條件的資料!"}
    '''
    url = 'https://www.twse.com.tw/exchangeReport/STOCK_DAY'
    date = year + month + '01'
    payload = {'response':'jason', 'date':date, 'stockNo':stock_id}
    
    res = requests.get(url, params=payload)
    return res.json()

