'''
提供操作資料庫的簡易界面
[import]
    warnings
    mysql_cmd
    pandas as pd
[param]
    columns_condition
[class]
    mysql_interface
'''

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

import mysql_cmd
import pandas as pd

# 用於條件判斷，詳見:mysql_cmd
columns_condition=mysql_cmd.create_condition_cmd()

class mysql_interface:
    '''mysql操作界面'''
    
    def __init__(self, conn, tab):
        '''
        [param]
        pymysql.connections.Connection conn: pymysql資料庫連接
        str tab: 資料表名稱
        '''
        self.conn=conn
        self.cmd_if=mysql_cmd.create_main_cmd(tab)
    
    def __getitem__(self, cmd):
        '''
        根據指令(cmd)取得資料表中資料
        [param]
            mysql_cmd.basic_cmd cmd: 執行cmd.command的指令
            int cmd:                 執行"SELECT * FROM {} Limit {}"
            slice cmd:               執行"SELECT * FROM {} Limit {}"
            str cmd:                 執行str的指令
        [return]
            pd.DataFrame
        '''
        if isinstance(cmd,mysql_cmd.basic_cmd):
            new_cmd=self.cmd_if.select().where(cmd)
            
        elif type(cmd)==int:
            # if len(self) = 3
            # exp1: cmd=1  => "Limit 1,1"
            # exp2: cmd=-1 => "Limit 2,1"
            idx=range(len(self))[cmd]
            new_cmd=self.cmd_if.select().limit([idx,1])
            
        elif type(cmd)==slice:
            # if len(self) = 3
            # exp1: cmd=[0:2]  => "Limit 0,2"
            # exp2: cmd=[-1:]  => "Limit 2,1"
            r=range(len(self))[cmd]
            start=r.start
            step=r.stop-r.start
            new_cmd=self.cmd_if.select().limit([start,step])
            
        else:
            new_cmd=self.cmd_if.select(cmd)
        
        return self.read_df(new_cmd)
    
    def __len__(self):
        '''
        取得資料表的資料筆數
        [return] int
        '''
        cmd=self.cmd_if.select('COUNT(*)')
        df=self.read_df(cmd)
        return df['COUNT(*)'][0]
    
    @property
    def columns_info(self):
        ''''
        取得資料表欄位比較詳細的訊息
        [return] pd.DataFrame
        '''
        cmd=self.cmd_if.show_tab('COLUMNS')
        return self.read_df(cmd)
    
    @property
    def columns(self):
        '''
        取得資料表的欄位list
        [return] plist
        '''
        df=self.columns_info
        return list(df['Field'])
    
    def commit(self, cmd_list):
        '''
        執行裝有指令的list中的指令
        [param]
        list[mysql_cmd.basic_cmd] cmd_list
        list[str] cmd_list
        '''
        with self.conn.cursor() as cursor:
            for cmd in cmd_list:
                if isinstance(cmd,mysql_cmd.basic_cmd):
                    cursor.execute(cmd.command)
                else: cursor.execute(cmd)
                
            self.conn.commit()
    
    def fetch(self, cmd, n=None):
        '''
        執行指令並取得回傳資料
        [param]
        mysql_cmd.basic_cmd cmd
        str cmd
        None n: 回傳全部結果
        int n:  回傳前幾筆結果
        '''
        with self.conn.cursor() as cursor:
            if isinstance(cmd,mysql_cmd.basic_cmd):
                cursor.execute(cmd.command)
            else: cursor.execute(cmd)
            
            if n is None: return cursor.fetchall()
            return cursor.fetchmany(n)
    
    def insert_df(self, df):
        '''
        將df插入到資料表中
        [param]
        pd.DataFrame df
        '''
        col_list=list(df.columns)
        insert_cmd=self.cmd_if.insert(col_list)
        
        commit_list=[]
        for idx, row in df.iterrows():
            row=row.dropna()
            insert_cmd=self.cmd_if.insert(list(row.index))
            cmd=insert_cmd.values(list(row.array))
            
            commit_list.append(cmd)
        
        self.commit(commit_list)
    
    def read_df(self, cmd):
        '''
        執行cmd中的指令，並將回傳資料以DataFrame的形式取出
        [param]
        mysql_cmd.basic_cmd cmd
        str cmd
        '''
        if isinstance(cmd,mysql_cmd.basic_cmd):
            return pd.read_sql(cmd.command, con=self.conn)
        return pd.read_sql(cmd, con=self.conn)