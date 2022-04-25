'''
操作特定資料表的界面
[import]
    mysql_interface as sqlif
    pymysql
[param]
    DEFAULT_HOST
    DEFAULT_PORT
[class]
    staff_tab_portal
    twse_pv_portal
'''

import mysql_interface as sqlif
import pymysql

DEFAULT_HOST='192.168.0.103'
DEFAULT_PORT=3306

class staff_tab_portal(sqlif.mysql_interface):
    def __init__(self, user, password, host=DEFAULT_HOST, port=DEFAULT_PORT):
        bd_name='stock_db'
        tab_name='staff_tab'
        conn=pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=bd_name
        )
        
        super().__init__(conn=conn, tab=tab_name)

class twse_pv_portal(sqlif.mysql_interface):
    def __init__(self, user, password, host=DEFAULT_HOST, port=DEFAULT_PORT):
        bd_name='stock_db'
        tab_name='twse_pv'
        conn=pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=bd_name
        )
        
        super().__init__(conn=conn, tab=tab_name)