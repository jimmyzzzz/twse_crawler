'''
爬蟲函數會用到的裝飾器
[import]
    os
    datetime import datetime
    time
    pickle
[def]
    if_not_exists_then_makefile
    record_error_decorator
    try_loop_decorator
    backup_decorator
[class]
    decorator_error
    run_func_error
    record_log_error
'''

import os

def if_not_exists_then_makefile(path):
    '''如果檔案不存在就新建該檔案'''
    
    # 如果檔案存在
    if os.path.exists(path): return

    dir_path,file_name = os.path.split(path)
    
    # 建立資料夾
    if dir_path != '': os.makedirs(dir_path)
    
    # 建立檔案
    f=open(path, 'w')
    f.close()


class decorator_error:
    '''<catch_error_and_record_decorator> 發生的錯誤'''
    pass

class run_func_error(decorator_error):
    '''裝飾器的函數發生了運行錯誤'''
    pass

class record_log_error(decorator_error):
    '''裝飾器在保存錯誤訊息時發生了錯誤'''
    pass


from datetime import datetime

def record_error_decorator(log_path='error.log'):
    '''
    用來紀錄函數運行錯誤的裝飾器
    [param]
        str log_path:     如果函數報錯，保存錯誤的路徑
    [return]
        func(...):        函數沒報錯，回傳函數的回傳值
        run_func_error:   函數報錯，保存錯誤訊息成功
        record_log_error: 函數報錯，保存錯誤訊息失敗
    '''
    
    # 如果檔案不存在就新建該檔案
    if_not_exists_then_makefile(log_path)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            
            except Exception as error:
                # 報錯時間
                now_time=datetime.now()
                now_time_str=datetime.strftime(now_time,'%Y%m%d %H:%M:%S')
                
                # 錯誤的函數名＆錯誤訊息
                func_name=func.__name__
                error_message=str(error)
                
                # 紀錄的錯誤訊息
                record_message_str=f"[{now_time_str}] {func_name}: {error_message}\n"
                
                # 添加錯誤訊息到log中
                with open(log_path, 'a+', encoding='utf-8') as f:
                    f.writelines(record_message_str)
                    return run_func_error()
                
                # 如果添加錯誤訊息失敗
                return record_log_error()
            
        return wrapper
    return decorator


import time

def try_loop_decorator(times=3, sleep_time=2):
    '''
    當函數回傳裝飾器錯誤類別時，重跑函數幾次的裝飾器
    [param]
        int times:           最多重跑幾次
        int sleep_time:      每次重跑後休息幾秒
    [return]
        decorator_error.sub
        func(...)       
    '''
    def decorator(func):
        def wrapper(*args, **kwargs):
            for idx in range(times):
                func_return=func(*args, **kwargs)
                time.sleep(sleep_time)
                
                # 如果函數順利運行，沒有回傳錯誤物件
                if not isinstance(func_return, decorator_error):
                    return func_return
                
            # 如果到最後都沒有順利運行
            return func_return
            
        return wrapper
    return decorator


import pickle

def backup_decorator(backup_path):
    '''
    當函數抓不到資料時，可以使用之前抓的備份資料替代
    *備份資料使用pickle保存
    [param]
        str backup_path:   備份檔案路徑
    [return]
    [exception]
        Exception:         func報錯
        FileNotFoundError: 備份檔案無法開啟
    '''
    
    # 如果檔案不存在就新建該檔案
    if_not_exists_then_makefile(backup_path)
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            
            func_return=func(*args, **kwargs)
            
            if isinstance(func_return, decorator_error):
                f=open(backup_path, 'rb')
                backup_data = pickle.load(f)
                return backup_data
            
            else:
                with open(backup_path, 'wb') as f:
                    pickle.dump(func_return, f)
                return func_return
            
        return wrapper
    return decorator