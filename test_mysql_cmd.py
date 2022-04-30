

import unittest
import mysql_tool.mysql_cmd as mysql_cmd
import numpy as np

format_str=mysql_cmd.format_str
join_slist=mysql_cmd.join_slist
create_condition_cmd=mysql_cmd.create_condition_cmd
create_main_cmd=mysql_cmd.create_main_cmd

condition_cmd=mysql_cmd.condition_cmd
main_cmd=mysql_cmd.main_cmd

class func_test(unittest.TestCase):
    
    def test_format_str(self):
        self.assertEqual(format_str("xxx xx"), "'xxx xx'")
        self.assertEqual(format_str(np.nan), "NULL")
        self.assertEqual(format_str(None), "NULL")
        self.assertEqual(format_str(123),"123")
        
    def test_join_slist(self):
        self.assertEqual(join_slist([1,2,3]), "1, 2, 3")
        self.assertEqual(join_slist([1,'2','xxx xx']), "1, '2', 'xxx xx'")

class create_condition_cmd_test(unittest.TestCase):
    
    def setUp(self):
        self.cmd=create_condition_cmd()

    def test_1(self):
        new_cmd=self.cmd['id']
        self.assertIsInstance(new_cmd, condition_cmd)
        self.assertEqual(new_cmd.command, 'id')
    
    def test_2(self):
        new_cmd=self.cmd.id
        self.assertIsInstance(new_cmd, condition_cmd)
        self.assertEqual(new_cmd.command, 'id')

class create_main_cmd_test(unittest.TestCase):
    
    def setUp(self):
        self.cmd=create_main_cmd('table_name')
        
    def test_1(self):
        self.assertIsInstance(self.cmd, main_cmd)
    
    def test_2(self):
        self.assertEqual(self.cmd.table, 'table_name')
        self.assertEqual(self.cmd.command, '')

class condition_test(unittest.TestCase):
    def setUp(self):
        self.cmd=condition_cmd('col_name')
        
    def test_col_name(self):
        self.assertEqual(self.cmd.command, 'col_name')
        
    def test_computing_command(self):
        other1='other 1'
        other2=123
        symbol='symbol'
        
        result1=self.cmd.computing_command(other1,symbol)
        answer1="col_name symbol 'other 1'"
        self.assertEqual(result1, answer1)
        
        result2=self.cmd.computing_command(other2,symbol)
        answer2="col_name symbol 123"
        self.assertEqual(result2, answer2) 
        
    def test_computing(self):
        other_int=123
        other_float=12.3
        other_str='other str'
        
        cmd=self.cmd<other_int
        self.assertIsInstance(cmd, condition_cmd)
        
        # __lt__
        int_cmd=self.cmd<other_int
        self.assertEqual(int_cmd.command, "col_name < 123")
        
        float_cmd=self.cmd<other_float
        self.assertEqual(float_cmd.command, "col_name < 12.3")
        
        str_cmd=self.cmd<other_str
        self.assertEqual(str_cmd.command, "col_name < 'other str'")
        
        # __le__
        int_cmd=self.cmd<=other_int
        self.assertEqual(int_cmd.command, "col_name <= 123")
        
        float_cmd=self.cmd<=other_float
        self.assertEqual(float_cmd.command, "col_name <= 12.3")
        
        str_cmd=self.cmd<=other_str
        self.assertEqual(str_cmd.command, "col_name <= 'other str'")
        
        # __eq__
        int_cmd=self.cmd==other_int
        self.assertEqual(int_cmd.command, "col_name = 123")
        
        float_cmd=self.cmd==other_float
        self.assertEqual(float_cmd.command, "col_name = 12.3")
        
        str_cmd=self.cmd==other_str
        self.assertEqual(str_cmd.command, "col_name = 'other str'")
        
        # __eq__
        int_cmd=self.cmd!=other_int
        self.assertEqual(int_cmd.command, "col_name != 123")
        
        float_cmd=self.cmd!=other_float
        self.assertEqual(float_cmd.command, "col_name != 12.3")
        
        str_cmd=self.cmd!=other_str
        self.assertEqual(str_cmd.command, "col_name != 'other str'")
        
        # __gt__
        int_cmd=self.cmd>other_int
        self.assertEqual(int_cmd.command, "col_name > 123")
        
        float_cmd=self.cmd>other_float
        self.assertEqual(float_cmd.command, "col_name > 12.3")
        
        str_cmd=self.cmd>other_str
        self.assertEqual(str_cmd.command, "col_name > 'other str'")
        
        # __ge__
        int_cmd=self.cmd>=other_int
        self.assertEqual(int_cmd.command, "col_name >= 123")
        
        float_cmd=self.cmd>=other_float
        self.assertEqual(float_cmd.command, "col_name >= 12.3")
        
        str_cmd=self.cmd>=other_str
        self.assertEqual(str_cmd.command, "col_name >= 'other str'")
        
        # is_null
        null_cmd=self.cmd.is_null()
        self.assertEqual(null_cmd.command, "col_name IS NULL")
        
        # no_null
        null_cmd=self.cmd.no_null()
        self.assertEqual(null_cmd.command, "col_name IS NOT NULL")
    
    def test_isin_and_noin(self):
        other_int=123
        other_float=12.3
        other_str='other str'
        other_list=[other_int,other_float,other_str]
        other_cmd=main_cmd(table='tab', command='command xxx')
        
        # isin
        cmd=self.cmd.isin(other_int)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name IN (123)")
        
        cmd=self.cmd.isin(other_float)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name IN (12.3)")
        
        cmd=self.cmd.isin(other_str)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name IN ('other str')")
        
        cmd=self.cmd.isin(other_list)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name IN (123, 12.3, 'other str')")
        
        cmd=self.cmd.isin(other_cmd)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name IN (command xxx)")
        
        # noin
        cmd=self.cmd.noin(other_int)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name NOT IN (123)")
        
        cmd=self.cmd.noin(other_float)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name NOT IN (12.3)")
        
        cmd=self.cmd.noin(other_str)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name NOT IN ('other str')")
        
        cmd=self.cmd.noin(other_list)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name NOT IN (123, 12.3, 'other str')")
        
        cmd=self.cmd.noin(other_cmd)
        self.assertIsInstance(cmd, condition_cmd)
        self.assertEqual(cmd.command, "col_name NOT IN (command xxx)")
        
    def test_and_or(self):
        cmd1=condition_cmd("col1 > 123")
        cmd2=condition_cmd("col2 = 'xx xxx'")
        
        and_cmd=cmd1&cmd2
        and_answer="col1 > 123 AND col2 = 'xx xxx'"
        self.assertIsInstance(and_cmd, condition_cmd)
        self.assertEqual(and_cmd.command, and_answer)
        
        or_cmd=cmd1|cmd2
        or_answer="col1 > 123 OR col2 = 'xx xxx'"
        self.assertIsInstance(and_cmd, condition_cmd)
        self.assertEqual(or_cmd.command, or_answer)
        
class main_cmd_test(unittest.TestCase):
    
    def setUp(self):
        self.cmd=main_cmd(table='table', command='')
    
    def test_init(self):
        self.assertIsInstance(self.cmd, main_cmd)
        self.assertEqual(self.cmd.table, 'table')
        self.assertEqual(self.cmd.command, '')
        
    def test_insert(self):
        cmd=self.cmd.insert(['col'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col)")
        
        cmd=self.cmd.insert(['col1', 'col2'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col1, col2)")
        
    
    def test_values(self):
        cmd=self.cmd.insert(['col']).values([1])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col) VALUES(1)")
        
        cmd=self.cmd.insert(['col']).values([1.2])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col) VALUES(1.2)")
        
        cmd=self.cmd.insert(['col']).values(['xx x'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col) VALUES('xx x')")
        
        cmd=self.cmd.insert(['col1','col2']).values([np.nan,None])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "INSERT INTO table(col1, col2) VALUES(NULL, NULL)")
        
        cmd=self.cmd.insert(['col1','col2','col3']).values([1,1.2,'xx x'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(
            cmd.command,
            "INSERT INTO table(col1, col2, col3) VALUES(1, 1.2, 'xx x')"
        )
        
    def test_select(self):
        cmd=self.cmd.select()
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT * FROM table")
        
        cmd=self.cmd.select('col')
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT col FROM table")
        
        cmd=self.cmd.select(['col1','col2'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT col1, col2 FROM table")
        
    def test_where(self):
        cmd=self.cmd.select().where("id = 5")
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT * FROM table WHERE id = 5")
        
        condition=condition_cmd('col')>1.5
        cmd=self.cmd.select().where(condition)
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT * FROM table WHERE col > 1.5")
        
        condition=condition_cmd('col')=='xx x'
        cmd=self.cmd.select().where(condition)
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT * FROM table WHERE col = 'xx x'")
        
    def test_update(self):
        cmd=self.cmd.update({'col1':1, 'col2':1.2, 'col3':'xx x'})
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(
            cmd.command,
            "UPDATE table SET col1 = 1, col2 = 1.2, col3 = 'xx x'"
        )
        
        cmd=self.cmd.update({'col1':np.nan, 'col2':None})
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(
            cmd.command,
            "UPDATE table SET col1 = NULL, col2 = NULL"
        )
    
    def test_delet(self):
        cmd=self.cmd.delet.where('id = 1')
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "DELETE FROM table WHERE id = 1")
        
    def test_order_by(self):
        cmd=self.cmd.select('col').order_by(
            col_list=['col1','col2','col3'],desc_list=['col2']
        )
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, 
            "SELECT col FROM table ORDER BY col1 ASC, col2 DESC, col3 ASC"
        )
        
    def test_limit(self):
        cmd=self.cmd.select('col').limit([1,2,3])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT col FROM table Limit 1, 2, 3")
        
    def test_show_tab(self):
        cmd=self.cmd.show_tab('col')
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SHOW col FROM table")
        
        cmd=self.cmd.show_tab(['col1','col2'])
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SHOW col1, col2 FROM table")
        
    def test_union_and_union_all(self):
        cmd=self.cmd.select('col1').union.select('col2')
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT col1 FROM table UNION SELECT col2 FROM table")
        
        cmd=self.cmd.select('col1').union_all.select('col2')
        self.assertIsInstance(cmd, main_cmd)
        self.assertEqual(cmd.command, "SELECT col1 FROM table UNION ALL SELECT col2 FROM table")
        
if __name__ == '__main__':
    unittest.main()