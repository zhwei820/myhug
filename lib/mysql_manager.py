# -*- coding: UTF-8 -*-
"""
mysql连接管理类

主要目标：
带读写分离，带多读库支持

@author: zh
"""
import MySQLdb
import _mysql_exceptions
import warnings
import traceback
import MySQLdb.cursors
from decouple import config
import dj_database_url
from lib.logger import info, error

class Mysql:

    default_charset = "utf8"

    def __init__(self, db_name=""):
        self.db_name = db_name
        self.auto_commit = False

        self.db = None
        self.cur = None

    def get_conn(self, db_name='', auto_commit=True):
        if self.db is None:
            self.auto_commit = auto_commit
            # 主库 读写
            if not self.db_name:
                dbConf = dj_database_url.config(default = config('DATABASE_URL', default='mysql://root:spwx@localhost:3306/pinax_mysite'))
            if self.db_name:
                dbConf = dj_database_url.config(default = config('DATABASE_URL_' + db_name, default='mysql://root:spwx@localhost:3306/pinax_mysite'))
            self.db = MySQLdb.Connect(host=dbConf['HOST'], user=dbConf['USER'],
                                      passwd=dbConf['PASSWORD'], port=int(dbConf['PORT']),
                                      db=dbConf['NAME'], charset=self.default_charset,
                                      cursorclass=MySQLdb.cursors.DictCursor)
            self.db.autocommit(self.auto_commit)
            self.cur = self.db.cursor()
        elif auto_commit != self.auto_commit:
            self.auto_commit = auto_commit
            self.db.autocommit(auto_commit)

    @staticmethod
    def F(sql):
        # 格式化字符串，避免sql攻击
        return MySQLdb.escape_string(sql)

    def SQ(self, sql, args=None):
        return self._query(sql, args)

    # 普通方式请求数据库
    def Q(self, sql, args=None):
        return self._query(sql, args)


    def worker(self, sql_list=None, callback=None):
        rs = False
        if not sql_list:
            return rs

        self.db.autocommit(False)
        try:
            for sql in sql_list:
                self.Q(sql)

            self.db.commit()
            # 放个钩子
            if callback:
                callback()

            rs = True
        except:
            error("worker error: ", exc_info=True)
            self.db.rollback()
            rs = False
        finally:
            self.db.autocommit(True)
        return rs

    # 事物需要TQ支持 而不是Q
    def TQ(self, sql, args=None):
        try:
            self.get_conn(False)
            rs = self.cur.execute(sql, args)
            return rs
        except MySQLdb.Error as e:
            error("_query error: %s %s", sql, args, exc_info=True)
            raise e

    def _query(self, sql, args=None):

        try:
            self.get_conn()
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter('always')
                rs = self.cur.execute(sql, args)
                if w:
                    pass
            return rs
        except MySQLdb.Error as e:
            e.args = (e.args, sql, args)
            raise e

    def fetch_one(self):
        return self.cur.fetchone()

    def fetch_all(self):
        return self.cur.fetchall()

    def executemany(self, sql, args):
        u'''批量执行多sql语句
        '''
        rslt = None
        try:
            self.get_conn(False)
            rslt = self.cur.executemany(sql, args)
            self.db.commit()
        except (_mysql_exceptions.DatabaseError, _mysql_exceptions.OperationalError, _mysql_exceptions.ProgrammingError) as e:
            error('got Exception when do sql:%s, (total:%d)args[:5]=%s, e:\n%s', sql, len(args), args[:5], e)
            self.db.rollback()
            raise e
        except StandardError as e:
            info('got StandardError and rollback when do sql:%s, (total:%d)args[:5]=%s, e:\n%s', sql, len(args), args[:5], e)
            self.db.rollback()
            raise e
        except Exception as e:
            info('got Exception and rollback when do sql:%s, (total:%d)args[:5]=%s, e:\n%s', sql, len(args), args[:5], e)
            self.db.rollback()
            raise e

        return rslt

    def close(self):
        try:
            self.cur.close()
        except:
            pass
        try:
            self.db.close()
        except:
            pass
        finally:
            self.db = None

    def __del__(self):
        try:
            if self.db is not None:
                self.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 添加对with语句的支持
        try:
            if self.cur:
                self.cur.close()
        except:
            pass

        try:
            if self.db:
                self.close()
        except:
            pass

        if exc_type:
            error('%s', traceback.format_exc())
        return True  # suppress exception

    def insert_id(self):
        return self.cur.lastrowid
