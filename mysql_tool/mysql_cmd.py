'''
使用物件的方式產生mysql指令
[import]
    numpy as np
[def]
    format_str
    join_slist
    create_cmd
    
[class]
    basic_cmd
    condition_cmd <-basic_cmd
    main_cmd      <-basic_cmd
'''

import numpy as np

def format_str(x):
    '''修改字串的內容，方便轉換成mysql指令'''
    if type(x)==str: return f"'{x}'"
    if x is None: return 'NULL'
    if np.isnan(x): return 'NULL'
    return str(x)

def join_slist(slist):
    '''修改list中的字串的內容，方便轉換成mysql指令'''
    join_list=[format_str(s) for s in slist]
    return ', '.join(join_list)

class basic_cmd:
    '''cmd的基本類'''
    def __init__(self):
        self.command=''
    
    def __repr__(self):
        return f"cmd({self.command.__repr__()})"
        
class condition_cmd(basic_cmd):
    '''
    增加條件判斷的功能
    
    操作1:   cls('id')==1
    產生指令: "id = 1"
    
    操作2:   (cls('id')>1) & (cls('name')=='jimmy zzzz')
    產生指令: "id > 1 AND name = 'jimmy zzzz'"
    
    '''
    def __init__(self,col_name):
        self.command=col_name
    
    def computing_command(self, other, symbol):
        other_str=format_str(other)
        return f"{self.command} {symbol} {other_str}"
    
    def __lt__(self, other):
        command=self.computing_command(other,'<')
        return type(self)(command)
    
    def __le__(self, other):
        command=self.computing_command(other,'<=')
        return type(self)(command)
    
    def __eq__(self, other):
        command=self.computing_command(other,'=')
        return type(self)(command)
        
    def __ne__(self, other):
        command=self.computing_command(other,'!=')
        return type(self)(command)
        
    def __gt__(self, other):
        command=self.computing_command(other,'>')
        return type(self)(command)
        
    def __ge__(self, other):
        command=self.computing_command(other,'>=')
        return type(self)(command)
    
    def is_null(self):
        command=self.computing_command(np.nan,'IS')
        return type(self)(command)
    
    def no_null(self):
        command=self.computing_command(np.nan,'IS NOT')
        return type(self)(command)
    
    def isin(self, other):
        '''
        [param]
        int/float/str other
        list other
        main_cmd other
        '''
        if type(other)==main_cmd:
            command=f"{self.command} IN ({other.command})"
            return type(self)(command)
        elif type(other)==list:
            other_str=join_slist(other)
            command=f"{self.command} IN ({other_str})"
            return type(self)(command)
        
        # other: 數字 or str
        other_str=format_str(other)
        command=f"{self.command} IN ({other_str})"
        return type(self)(command)
    
    def noin(self, other):
        '''
        [param]
        int/str other
        list other
        main_cmd other
        '''
        if type(other)==main_cmd:
            command=f"{self.command} NOT IN ({other.command})"
            return type(self)(command)
        elif type(other)==list:
            other_str=join_slist(other)
            command=f"{self.command} NOT IN ({other_str})"
            return type(self)(command)
        
        # other: 數字 or str
        other_str=format_str(other)
        command=f"{self.command} NOT IN ({other_str})"
        return type(self)(command)
    
    def __and__(self, other):
        '''
        [param] condition_cmd other
        '''
        command=f"{self.command} AND {other.command}"
        return type(self)(command)
    
    def __or__(self, other):
        '''
        [param] condition_cmd other
        '''
        command=f"{self.command} OR {other.command}"
        return type(self)(command)
    
    

class main_cmd(basic_cmd):
    '''增加基本指令的功能'''
    def __init__(self, table, command):
        '''
        [param]
            str table:   資料表名稱
            str command: 要添加在前面的指令
        '''
        self.table=table
        self.command=command
    
    def insert(self, col_list):
        '''
        [param] list col_list: 欄位的列表
        '''
        col_str=', '.join(col_list)
        new_command=f"{self.command}INSERT INTO {self.table}({col_str})"
        return type(self)(self.table, new_command)
    
    def values(self, value_list):
        values_str=join_slist(value_list)
        new_command=f"{self.command} VALUES({values_str})"
        return type(self)(self.table, new_command)
    
    def select(self, col='*'):
        col=', '.join(col) if type(col)==list else col
        new_command=f"{self.command}SELECT {col} FROM {self.table}"
        return type(self)(self.table, new_command)
    
    def where(self, condition):
        condition=condition.command if isinstance(condition,basic_cmd) else condition
        new_command=f"{self.command} WHERE {condition}"
        return type(self)(self.table, new_command)
    
    def update(self, update_dict):
        kv_format=lambda key,value: f"{key} = {format_str(value)}"
        update_str=', '.join(kv_format(k,v) for k,v in update_dict.items())
        new_command=f"{self.command}UPDATE {self.table} SET {update_str}"
        return type(self)(self.table, new_command)
    
    @property
    def delet(self):
        new_command=f"{self.command}DELETE FROM {self.table}"
        return type(self)(self.table, new_command)
    
    def order_by(self, col_list, desc_list=[]):
        new_command=', '.join([
            f"{col} DESC" if col in desc_list else f"{col} ASC" 
            for col in col_list
        ])
        new_command=f"{self.command} ORDER BY {new_command}"
        return type(self)(self.table, new_command)
    
    def limit(self, int_list):
        '''
        [param]
            list[int] int_list:
                [1]   => "Limit 1"
                [1,2] => "Limit 1, 2"
        '''
        join_str=join_slist(int_list)
        new_command=f"{self.command} Limit {join_str}"
        return type(self)(self.table, new_command)
    
    def show_tab(self, col):
        col=', '.join(col) if type(col)==list else col
        new_command=f"{self.command}SHOW {col} FROM {self.table}"
        return type(self)(self.table, new_command)
    
    @property
    def union(self):
        new_command=f"{self.command} UNION "
        return type(self)(self.table, new_command)
    
    @property
    def union_all(self):
        new_command=f"{self.command} UNION ALL "
        return type(self)(self.table, new_command)
    
    
def create_condition_cmd():
    '''產生condition_cmd的實例'''
    class condition_creater:
        def __getitem__(self, col_name):
            return condition_cmd(col_name)
        def __getattr__(self, col_name):
            return condition_cmd(col_name)
    return condition_creater()
        
def create_main_cmd(table_name):
    '''產生main_cmd的實例'''
    return main_cmd(table_name, '')

