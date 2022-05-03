'''
每日抓取0050成份股的資料並保存到資料表twse_stock中
[import]
    from crawler_tool:
        record_error_decorator
        try_loop_decorator
        backup_decorator
        decorator_error
        get_latest_trading_days
        get_0050_list
        get_day_price
        twse_stock_portal
    from datetime import datetime
    pandas as pd
    time
[def]
    today_is_trading_days
    get_stock_list
    daily_crawler
    daily_df_to_twse_tab
    main
'''
from crawler_tool import record_error_decorator
from crawler_tool import try_loop_decorator
from crawler_tool import backup_decorator
from crawler_tool import decorator_error

from datetime import datetime
from crawler_tool import get_latest_trading_days

def today_is_trading_days(now_date):
    '''
    確認now_date是不是最近一次的交易日
    [param] datetime now_date: 今天日期
    [return] bool
    '''
    @try_loop_decorator(times=5, sleep_time=3)
    @record_error_decorator('daily_error.log')
    def latest_trading_days_crawler():
        return get_latest_trading_days()
    
    date_str=latest_trading_days_crawler()
    if isinstance(date_str,decorator_error):
        return True
    
    if date_str==datetime.strftime(now_date,'%Y%m%d'):
        return True
    return False

from crawler_tool import get_0050_list

def get_stock_list():
    '''
    取得0050的成份股名單
    [return] list[str] or []
    '''
    @backup_decorator(backup_path='backup_0050list.pickle')
    @try_loop_decorator(times=5, sleep_time=3)
    @record_error_decorator(log_path='daily_error.log')
    def get_list():
        return get_0050_list()
    
    ret_list=get_list()
    if isinstance(ret_list,decorator_error):
        return []
    return ret_list

from crawler_tool import get_day_price
import pandas as pd

@record_error_decorator('daily_error.log')
def daily_crawler(stock_list, now_date):
    '''
    根據股票名單爬取股價資料
    [param]
        list[str] stock_list: 要抓資料的股票名單
        datetime now_date:    抓的資料的日期
    [return]
        (DataFrame, int):     (股價資料df, 成功抓到資料的股票數)
        decorator_error:      運作時發生錯誤
    '''
    year,month,day=now_date.year,now_date.month,now_date.day
    
    empty_df=pd.DataFrame()
    total_df=pd.DataFrame()
    success_count=0
    for stock_id in stock_list:
        df=get_day_price(stock_id, year, month, day, None)
        
        if df is None: continue
        
        success_count+=1
        total_df=pd.concat([total_df,df],axis=0,ignore_index=True)
        
    return total_df, success_count


from mysql_tool import twse_stock_portal

@record_error_decorator('daily_error.log')
def daily_df_to_twse_tab(df):
    '''
    將資料插入到資料表twse_stock
    [param]
        pd.DataFrame df: 要插入的資料
    [return]
        None:            運作正常
        decorator_error: 運作時發生錯誤
    '''
    twse_tab=twse_stock_portal(user='testuser', password='123')
    twse_tab.insert_df(df)


import time    

@record_error_decorator('daily_error.log')
def main():
    '''
    抓取資料並插入到資料庫中
    *也會保存一份到daily_df.csv中
    '''
    # 可以在這修改要抓的資料期
    now_date=datetime.now()
    #now_date=datetime.strptime('2022-04-28','%Y-%m-%d')
    #date_str=datetime.strftime(now_date,'%Y%m%d %H:%M:%S')
     
    # 計時:開始
    time_start=time.time()
    
    # 確認今天是不是交易日
    if not today_is_trading_days(now_date):
        print(f"[{date_str}] No need to crawl today")
        return
    
    # 抓取資料df
    stock_list=get_stock_list()
    daily_data=daily_crawler(stock_list, now_date)
    
    # 計時:爬蟲結束
    crawler_time_end=time.time()
    
    # 如果爬蟲報錯(失敗)
    if isinstance(daily_data, decorator_error):
        print(f"[{date_str}] daily_crawler fail")
        print(f"crawler time cost: {(crawler_time_end-time_start)/3600}")
        return
    
    # 如果爬蟲成功
    df,success_count=daily_data
    print(f"[{date_str}] daily_crawler success:{success_count}/{len(stock_list)}")
    
    # 保存資料表(備份用)
    df.to_csv('daily_df.csv', index=False)
    
    # 保存資料表到資料庫中
    daily_df_to_twse_tab(df)
    
    # 計時:保存結束
    db_time_end=time.time()
    print(f"crawler time cost: {(crawler_time_end-time_start)/3600}",end=', ')
    print(f"db time cost: {(db_time_end-time_start)/3600}")

    
if __name__ == '__main__':
    main()
    