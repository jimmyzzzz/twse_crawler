


import unittest
from unittest.mock import patch, MagicMock

from mysql_tool.mysql_interface import mysql_interface
from mysql_tool.mysql_interface import columns_condition
import mysql_tool.mysql_cmd as mysql_cmd

main_cmd=mysql_cmd.main_cmd
condition=mysql_cmd.create_condition_cmd()

import pandas as pd
import numpy as np
import pymysql

class mocked_conn: pass  
class mocked_df: pass

class mysql_interface_test(unittest.TestCase):
    
    def setUp(self):
        self.conn=mocked_conn()
        self.IF=mysql_interface(self.conn, 'tab_name')
        
    def test_init(self):
        self.assertIsInstance(self.IF, mysql_interface)
        self.assertIsInstance(self.IF.conn, mocked_conn)
        self.assertIsInstance(self.IF.cmd_if, mysql_cmd.main_cmd)
    
    def test_len(self):
        with patch('mysql_tool.mysql_interface.read_df') as mocked_get:
            mocked_get.return_value=pd.DataFrame({'COUNT(*)':[123]})
            tab_size=len(self.IF)
            
            cmd=mocked_get.call_args.args[0]
            self.assertEqual(cmd.command, 'SELECT COUNT(*) FROM tab_name')
            self.assertEqual(tab_size, 123)

    def test_columns(self):
        with patch('mysql_tool.mysql_interface.read_df') as mocked_get:
            mocked_get.return_value=pd.DataFrame({'Field':['col1','col2']})
            col_list=self.IF.columns
            
            cmd=mocked_get.call_args.args[0]
            self.assertEqual(cmd.command, 'SHOW COLUMNS FROM tab_name')
            self.assertEqual(col_list, ['col1','col2'])
    
    def test_getitem(self):
        read_df_ret=mocked_df()
        
        with patch('mysql_tool.mysql_interface.read_df') as mocked_read_df:
            mocked_read_df.return_value=read_df_ret
            
            df=self.IF['col']
            cmd=mocked_read_df.call_args.args[0]
            self.assertEqual(df, read_df_ret)
            self.assertIsInstance(cmd, main_cmd)
            self.assertEqual(cmd.command, "SELECT col FROM tab_name")
            
            df=self.IF[condition.id==1]
            cmd=mocked_read_df.call_args.args[0]
            self.assertEqual(df, read_df_ret)
            self.assertIsInstance(cmd, main_cmd)
            self.assertEqual(cmd.command, "SELECT * FROM tab_name WHERE id = 1")
            
            with patch('mysql_tool.mysql_interface.__len__') as mocked_len:
                mocked_len.return_value=3
                
                df=self.IF[1]
                cmd=mocked_read_df.call_args.args[0]
                self.assertEqual(df, read_df_ret)
                self.assertIsInstance(cmd, main_cmd)
                self.assertEqual(cmd.command, "SELECT * FROM tab_name Limit 1, 1")
                
                df=self.IF[-1]
                cmd=mocked_read_df.call_args.args[0]
                self.assertEqual(df, read_df_ret)
                self.assertIsInstance(cmd, main_cmd)
                self.assertEqual(cmd.command, "SELECT * FROM tab_name Limit 2, 1")
                
                df=self.IF[0:2]
                cmd=mocked_read_df.call_args.args[0]
                self.assertEqual(df, read_df_ret)
                self.assertIsInstance(cmd, main_cmd)
                self.assertEqual(cmd.command, "SELECT * FROM tab_name Limit 0, 2")
                
                df=self.IF[-1:]
                cmd=mocked_read_df.call_args.args[0]
                self.assertEqual(df, read_df_ret)
                self.assertIsInstance(cmd, main_cmd)
                self.assertEqual(cmd.command, "SELECT * FROM tab_name Limit 2, 1")
    
    def test_commit(self):
        with patch('pymysql.connect') as mocked_conn:
            cursor=MagicMock()
            mocked_conn.return_value.cursor.return_value.__enter__.return_value=cursor
            
            # list[str]
            conn=pymysql.connect()
            mysql_interface(conn, 'tab_name').commit(['cmd1 xxx xx', 'cmd2 xxx xx'])
            
            command_list=list(map(lambda x:x.args[0], cursor.execute.call_args_list))
            called=mocked_conn.return_value.commit.called
            
            self.assertEqual(command_list, ['cmd1 xxx xx', 'cmd2 xxx xx'])
            self.assertEqual(called, True)
            
            # list[mysql_cmd.basic_cmd]
            mocked_conn.reset_mock()
            
            conn=pymysql.connect()
            cmd1=mysql_cmd.main_cmd('tab1','cmd1 xxx xx')
            cmd2=mysql_cmd.main_cmd('tab1','cmd2 xxx xx')
            mysql_interface(conn, 'tab_name').commit([cmd1, cmd2])
            
            command_list=list(map(lambda x:x.args[0], cursor.execute.call_args_list))
            called=mocked_conn.return_value.commit.called
            
            self.assertEqual(command_list, ['cmd1 xxx xx', 'cmd2 xxx xx'])
            self.assertEqual(called, True)
        
    def test_fetch(self):
        with patch('pymysql.connect') as mocked_conn:
            cursor=MagicMock()
            mocked_conn.return_value.cursor.return_value.__enter__.return_value=cursor
            
            class fetchall_ret: pass
            cursor.fetchall.return_value=fetchall_ret()
            class fetchmany_ret: pass
            cursor.fetchmany.return_value=fetchmany_ret()
            
            
            # cmd='cmd xxx xx', n=None
            conn=pymysql.connect()
            cmd='cmd xxx xx'
            response=mysql_interface(conn, 'tab_name').fetch(cmd)
            self.assertIsInstance(response, fetchall_ret)
                             
            command=cursor.execute.call_args.args[0]
            fetchall_called=cursor.fetchall.called
            fetchmany_called=cursor.fetchmany.called
            self.assertEqual(command, 'cmd xxx xx')
            self.assertEqual(fetchall_called, True)
            self.assertEqual(fetchmany_called, False)
            
            # cmd=mysql_cmd.basic_cmd, n=None
            mocked_conn.reset_mock()
            
            conn=pymysql.connect()
            cmd=mysql_cmd.main_cmd('tab1','cmd xxx xx')
            response=mysql_interface(conn, 'tab_name').fetch(cmd)
            self.assertIsInstance(response, fetchall_ret)
                             
            command=cursor.execute.call_args.args[0]
            fetchall_called=cursor.fetchall.called
            fetchmany_called=cursor.fetchmany.called
            self.assertEqual(command, 'cmd xxx xx')
            self.assertEqual(fetchall_called, True)
            self.assertEqual(fetchmany_called, False)
            
            # cmd='cmd xxx xx', n=5
            mocked_conn.reset_mock()
            
            conn=pymysql.connect()
            cmd='cmd xxx xx'; n=5
            response=mysql_interface(conn, 'tab_name').fetch(cmd, n)
            self.assertIsInstance(response, fetchmany_ret)
                             
            command=cursor.execute.call_args.args[0]
            get_n=cursor.fetchmany.call_args.args[0]
            fetchall_called=cursor.fetchall.called
            fetchmany_called=cursor.fetchmany.called
            self.assertEqual(command, 'cmd xxx xx')
            self.assertEqual(get_n, 5)
            self.assertEqual(fetchall_called, False)
            self.assertEqual(fetchmany_called, True)
            
            # cmd=mysql_cmd.basic_cmd, n=5
            mocked_conn.reset_mock()
            
            conn=pymysql.connect()
            cmd=mysql_cmd.main_cmd('tab1','cmd xxx xx'); n=5
            response=mysql_interface(conn, 'tab_name').fetch(cmd, n)
            self.assertIsInstance(response, fetchmany_ret)
                             
            command=cursor.execute.call_args.args[0]
            get_n=cursor.fetchmany.call_args.args[0]
            fetchall_called=cursor.fetchall.called
            fetchmany_called=cursor.fetchmany.called
            self.assertEqual(command, 'cmd xxx xx')
            self.assertEqual(get_n, 5)
            self.assertEqual(fetchall_called, False)
            self.assertEqual(fetchmany_called, True)
            
    def test_insert_df(self):
        with patch('mysql_tool.mysql_interface.commit') as mocked_get:
            df=pd.DataFrame({'col1':[1,2],'col2':[1.2,np.nan],'col3':['aa','b c']})
            self.IF.insert_df(df)
            
            commit_list=mocked_get.call_args.args[0]
            self.assertIsInstance(commit_list, list)
            self.assertIsInstance(commit_list[0], main_cmd)
            self.assertIsInstance(commit_list[1], main_cmd)
            
            self.assertEqual(
                commit_list[0].command, 
                "INSERT INTO tab_name(col1, col2, col3) VALUES(1, 1.2, 'aa')"
            )
            self.assertEqual(
                commit_list[1].command, 
                "INSERT INTO tab_name(col1, col2, col3) VALUES(2, NULL, 'b c')"
            )
            
if __name__ == '__main__':
    unittest.main()