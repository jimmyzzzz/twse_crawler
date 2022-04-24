'''
使用物件的方式產生mysql指令
[def]
    format_str
    create_cmd
[class]
    basic_cmd
    condition_cmd  <-basic_cmd
    main_cmd       <-condition_cmd
'''

def format_str(x):
    '''修改字串的內容，方便轉換成mysql指令'''
    return f"'{x}'" if type(x)==str else x

def join_slist(slist):
    join_list=[]
    for s in slist:
        if type(s)==str: join_list.append(format_str(s))
        else: join_list.append(str(s))
    return ', '.join(join_list)

class basic_cmd:
    '''cmd的基本類'''
    def __init__(self, table, command):
        '''
        [param]
            str table:   資料表名稱
            str command: 要添加在前面的指令
        '''
        self.table=table
        self.command=command
    
    def __repr__(self):
        return f"cmd({self.command.__repr__()})"
        
class condition_cmd(basic_cmd):
    '''
    增加條件判斷的功能
    
    操作1:   cmd['id']==1
    產生指令: "id = 1"
    
    操作2:   (cmd['id']>1) & (cmd['name']=='jimmy zzzz')
    產生指令: "id > 1 AND name = 'jimmy zzzz'"
    
    '''
    def __getitem__(self, col_str):
        new_command=col_str
        return type(self)(self.table, new_command)
    
    def new_command(self, other, symbol):
        other_str=format_str(other)
        return f"{self.command} {symbol} {other_str}"
    
    def __lt__(self, other):
        command=self.new_command(other,'<')
        return type(self)(self.table, command)
    
    def __le__(self, other):
        command=self.new_command(other,'<=')
        return type(self)(self.table, command)
    
    def __eq__(self, other):
        command=self.new_command(other,'=')
        return type(self)(self.table, command)
        
    def __ne__(self, other):
        command=self.new_command(other,'!=')
        return type(self)(self.table, command)
        
    def __gt__(self, other):
        command=self.new_command(other,'>')
        return type(self)(self.table, command)
        
    def __ge__(self, other):
        command=self.new_command(other,'>=')
        return type(self)(self.table, command)
    
    def __and__(self, other):
        command=f"{self.command} AND {other.command}"
        return type(self)(self.table, command)
    
    def __or__(self, other):
        command=f"{self.command} OR {other.command}"
        return type(self)(self.table, command)

class main_cmd(condition_cmd):
    '''增加基本指令的功能'''
    
    def insert(self, col_list):
        '''
        [param] list col_list: 欄位的列表
        '''
        col_str=', '.join(col_list)
        new_command=f"INSERT INTO {self.table}({col_str}) "
        return type(self)(self.table, new_command)
    
    def values(self, value_list):
        values_str=join_slist(value_list)
        new_command=self.command+f"VALUES({values_str})"
        return type(self)(self.table, new_command)
    
    def select(self, col='*'):
        col=', '.join(col) if type(col)==list else col
        new_command=f"SELECT {col} FROM {self.table}"
        return type(self)(self.table, new_command)
    
    def where(self, condition):
        condition=condition.command if isinstance(condition,basic_cmd) else condition
        new_command=f"{self.command} WHERE {condition}"
        return type(self)(self.table, new_command)
    
    def update(self, update_dict):
        kv_format=lambda key,value: f"{key} = {format_str(value)}"
        update_str=', '.join(kv_format(k,v) for k,v in update_dict.items())
        new_command=f"UPDATE {self.table} SET {update_str}"
        return type(self)(self.table, new_command)
    
    def delet(self):
        new_command=f"DELETE FROM {self.table}"
        return type(self)(self.table, new_command)
    
    def abs_order(self, col_name):
        new_command=f"{self.command} ORDER BY {col_name} ASC"
        return type(self)(self.table, new_command)
    
    def desc_order(self, col_name):
        new_command=f"{self.command} ORDER BY {col_name} DESC"
        return type(self)(self.table, new_command)
    
def create_cmd(table_name):
    '''產生指令的實例'''
    return main_cmd(table_name, '')