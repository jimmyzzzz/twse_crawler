'''
使用crawlers.get_stock_month_price爬取資料並處理格式，回傳DataFrame
*請使用get_df()取得資料
[param]
    TIMES=5
    SLEEP_TIME=3
    CRAWLER_LOG_PATH='stock_crawler_error.log'
    FORMAT_LOG_PATH='format_error.log'
[import]
    crawlers as cs
    crawler_decorator as cd
    numpy as np
    pandas as pd
[def]
    stock_crawler
    stock_df_format
    get_df
'''

import crawler_tool.crawlers as cs
import crawler_tool.crawler_decorator as cd
import numpy as np
import pandas as pd

# 定義詳見:stock_crawler
TIMES=5
SLEEP_TIME=3
CRAWLER_LOG_PATH='stock_crawler_error.log'

@cd.try_loop_decorator(times=TIMES, sleep_time=SLEEP_TIME)
@cd.record_error_decorator(CRAWLER_LOG_PATH)
def stock_crawler(stock_id, year, month):
    '''
    抓取股票月資料回傳DataFrame
    1. 呼叫cs.get_stock_month_price取得jason資料
    2. jason資料轉換成DataFrame
    3. 加入股票號碼欄位
    4. 去除「漲跌價差」欄位
    [param]
        int times:            爬蟲報錯後重新嘗試的次數
        int sleep_time:       重新嘗試間隔時間(秒)
        str CRAWLER_LOG_PATH: 爬蟲報錯後保存錯誤資訊的路徑
        str stock_id:         exp:'1101'
        str year:             exp:'2022'
        str month:            exp:'04'
    [return]
        pd.DataFrame          運作正常
        cd.run_func_error     解釋器接到報錯的回傳
        cd.record_log_error   解釋器寫入檔案錯誤的回傳
    '''
    # 呼叫cs.get_stock_month_price取得jason資料
    res_dict=cs.get_stock_month_price(stock_id, year, month)
    
    # 沒有報錯但沒有抓到資料
    if not 'data' in res_dict: raise ValueError('size=0')
    
    # jason資料轉換成DataFrame
    values_np=np.array(res_dict['data'])
    col_list=res_dict['fields']
    stock_df=pd.DataFrame(values_np, columns=col_list)
    
    # 加入股票代號欄位
    stock_df['股票代號']=stock_id
    
    # 去除「漲跌價差」欄位
    stock_df=stock_df.drop("漲跌價差", axis=1)
    return stock_df


from copy import deepcopy

# 定義詳見:stock_df_format
FORMAT_LOG_PATH='format_error.log'

@cd.record_error_decorator(FORMAT_LOG_PATH)
def stock_df_format(stock_df):
    '''
    整理stock_crawler回傳的DataFrame的格式
    1. 將欄位名稱變成英文的
    2. 修改date欄位的日期格式
    3. 數值化其他欄位
    [param]
        str FORMAT_LOG_PATH:   報錯後保存錯誤資訊的路徑
        pd.DataFrame stock_df: stock_crawler回傳的DataFrame
    [return]
        pd.DataFrame:          運作正常
        cd.run_func_error:     解釋器接到報錯的回傳
        cd.record_log_error:   解釋器寫入檔案錯誤的回傳
    '''
    new_df=deepcopy(stock_df)
    
    # 將欄位名稱變成英文的
    replace_dict={
        # 日期＆成交量
        '日期':'date', '成交股數':'volume', '成交金額':'value',
        # 開高低收
        '開盤價':'open','最高價':'high','最低價':'low','收盤價':'close',
        # 其他
        '成交筆數':'record','股票代號':'stock_id'
    }
    new_df.columns=list(map(replace_dict.__getitem__, new_df.columns))
    
    # 將date欄位的日期改成mysql格式
    # '110/01/04' -> '2021-01-04'
    def change_date_format(old_date):
        old_date_list = old_date.split('/')
        year = int(old_date_list[0])+1911
        return f"{year}-{old_date_list[1]}-{old_date_list[2]}"
    new_df['date']=new_df['date'].apply(change_date_format)
    
    # 將數值欄位的「,」去掉，如果是「--」則變成None
    # 最後數值化
    def change_value_format(old_str):
        if old_str=='--': return np.nan
        return old_str.replace(',','')
    new_df['volume'] = new_df['volume'].apply(lambda x: int(change_value_format(x)))
    new_df['value'] = new_df['value'].apply(lambda x: int(change_value_format(x)))
    new_df['open'] = new_df['open'].apply(lambda x: float(change_value_format(x)))
    new_df['high'] = new_df['high'].apply(lambda x: float(change_value_format(x)))
    new_df['low'] = new_df['low'].apply(lambda x: float(change_value_format(x)))
    new_df['close'] = new_df['close'].apply(lambda x: float(change_value_format(x)))
    new_df['record'] = new_df['record'].apply(lambda x: int(change_value_format(x)))
    
    return new_df


def int_formate_str(n):
    '''
    將數字變成標準格式的str
    exp: 1=>'01', '4'=>'04'
    [param] int/str n
    '''
    int_n=int(n)
    if int_n >= 10: return str(int_n)
    return '0'+str(int_n)

def get_month_df(stock_id, year, month, fail_return=None):
    '''
    取得twse抓到的月股價資料
    1. 整理參數格式
    2. 抓取資料DataFrame
    3. 整理DataFrame格式
    [param]
        str stock_id:     股票名稱: '1101'
        str/int year:     年份: '2022' or 2022
        str/int month:    月份: '4' or '04' or 4
        fail_return:      抓取失敗時回傳的結果
    [return]
        pd.DataFrame:     運作正常
        fail_return:      有報錯時
    '''
    # 整理參數格式:全部轉換成str
    year=str(year)
    month=int_formate_str(month)
    
    # 抓取資料DataFrame
    df=stock_crawler(stock_id, year, month,
        _message=(stock_id, year, month) # 報錯時保存的額外訊息
    )
    
    # 如果抓取成功，才整理DataFrame格式
    if isinstance(df, cd.decorator_error): return fail_return
    df=stock_df_format(df)
    
    # 如果整理DataFrame格式成功，才回傳
    if isinstance(df, cd.decorator_error): return fail_return
    return df

def get_day_df(stock_id, year, month, day, fail_return=None):
    '''
    取得twse抓到的日股價資料
    1. 整理參數格式
    2. 抓取月資料DataFrame
    3. 從月資料中取得日資料
    [param]
        str stock_id:     股票名稱: '1101'
        str/int year:     年份: '2022' or 2022
        str/int month:    月份: '4' or '04' or 4
        str/int day:      日期: '1' or '01' or 1
        fail_return:      抓取失敗時回傳的結果
    [return]
        pd.DataFrame:     運作正常
        fail_return:      有報錯時
    '''
    # 整理參數格式:轉換成str
    year=str(year)
    month=int_formate_str(month)
    day=int_formate_str(day)
    
    # 抓取月資料DataFrame
    class crawler_fail_return: pass
    df=get_month_df(stock_id, year, month, crawler_fail_return())
    
    # 如果抓取成功，則從月資料中取得日資料
    if isinstance(df, crawler_fail_return): return fail_return
    df=df[df['date']==f"{year}-{month}-{day}"]
    return df