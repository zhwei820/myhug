# coding=utf-8
if __name__ == '__main__':
    import os
    import sys
    par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
    sys.path.append(par_dir)

from lib.rc import cache
from lib.tools import tools
from lib import redisManager
from lib.logger import info, error

class MessageLib(object):
    """docstring for MessageLib"""

    @staticmethod
    @cache.cache()
    def get_id_list(last_msg_id, uid):
        m = tools.mysql_conn()
        m.Q("SELECT id FROM o_user_msg_00 WHERE id < %s AND uid = %s;", (last_msg_id, uid))  # 参数绑定防止sql注入
        res = m.fetch_all()
        return [item['id'] for item in res] if res else None

    @staticmethod
    @cache.cache()
    def get_msg_by_id(id):
        m = tools.mysql_conn()
        m.Q("SELECT id, uid, info_title, info_subtitle, content, share_msg, info_time, info_type, info_notify, status, end_time, click_url, button_text, url_images, share_url, category, icon, pid, package_name FROM o_user_msg_00 WHERE id = %s;", (id, ))  # 参数绑定防止sql注入
        res = m.fetch_one()
        return res

    @staticmethod
    @cache.cache()
    def get_msg_list(last_msg_id, uid):
        msg_ids = MessageLib.get_id_list(last_msg_id, uid)
        rs = []
        if msg_ids:
            for msg_id in msg_ids:
                rs.append(MessageLib.get_msg_by_id(msg_id))
        return rs

if __name__ == '__main__':
    print(MessageLib.get_msg_list(100, 10000000))
